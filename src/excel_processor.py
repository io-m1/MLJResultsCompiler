"""
Excel Processing Module
Handles loading, processing, and merging Excel files from SurveyHeart
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
import logging
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from src.validators import clean_name, clean_email, parse_score, validate_row_data
from src.color_config import get_fill_for_test, TEST_COLORS

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """Process and consolidate test results from multiple Excel files"""
    
    REQUIRED_COLUMNS = ['Full Name', 'Email', 'Score', 'Result', '%']
    
    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialize the Excel processor
        
        Args:
            input_dir (str): Directory containing input XLSX files
            output_dir (str): Directory for output files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.test_data = {}  # {test_num: {email: {name, score}}}
        
    def find_column_index(self, sheet, column_names: List[str]) -> Optional[int]:
        """
        Find the index of a column by any of the possible names
        
        Args:
            sheet: openpyxl worksheet
            column_names (List[str]): Possible column names to search for
            
        Returns:
            int: Column index (1-based) or None if not found
        """
        for row in sheet.iter_rows(min_row=1, max_row=1):
            for cell_idx, cell in enumerate(row, 1):
                if cell.value and any(name.lower() in str(cell.value).lower() for name in column_names):
                    return cell_idx
        return None
    
    def load_test_file(self, filepath: Path, test_number: int) -> bool:
        """
        Load a single test file and extract data
        
        Args:
            filepath (Path): Path to the test XLSX file
            test_number (int): Test number (1-5)
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Loading test {test_number} from {filepath.name}")
            wb = openpyxl.load_workbook(filepath, data_only=True)
            ws = wb.active
            
            # Find column indices
            name_col = self.find_column_index(ws, ['Full Name', 'Name', 'Participant'])
            email_col = self.find_column_index(ws, ['Email', 'E-mail', 'Email Address'])
            score_col = self.find_column_index(ws, ['Score', 'Result', '%', 'Percentage'])
            
            if not all([name_col, email_col, score_col]):
                logger.error(f"Could not find required columns in {filepath.name}")
                return False
            
            # Extract data
            self.test_data[test_number] = {}
            row_count = 0
            
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                full_name = clean_name(row[name_col - 1] if name_col <= len(row) else "")
                email = clean_email(row[email_col - 1] if email_col <= len(row) else "")
                score = parse_score(row[score_col - 1] if score_col <= len(row) else None)
                
                is_valid, error_msg = validate_row_data(full_name, email, score)
                
                if is_valid:
                    self.test_data[test_number][email] = {
                        'name': full_name,
                        'score': score
                    }
                    row_count += 1
                else:
                    logger.warning(f"Row {row_idx} in test {test_number}: {error_msg}")
            
            logger.info(f"Loaded {row_count} valid records from test {test_number}")
            wb.close()
            return True
            
        except Exception as e:
            logger.error(f"Error loading {filepath.name}: {str(e)}")
            return False
    
    def load_all_tests(self, max_tests: Optional[int] = None) -> int:
        """
        Load all test files from input directory dynamically
        
        Args:
            max_tests (int): Maximum number of tests to load. If None, loads all found tests.
            
        Returns:
            int: Number of tests successfully loaded
        """
        loaded_count = 0
        
        # Find all XLSX files and extract test numbers
        all_xlsx_files = sorted(self.input_dir.glob("*.xlsx"))
        test_nums = set()
        
        logger.info(f"Scanning {len(all_xlsx_files)} files in {self.input_dir}")
        
        for f in all_xlsx_files:
            # Extract test number from filename using flexible pattern
            test_num = self._extract_test_number_from_file(f.name)
            if test_num:
                test_nums.add(test_num)
                logger.debug(f"Found test {test_num} in file: {f.name}")
        
        logger.info(f"Found test numbers: {sorted(test_nums)}")
        
        if not test_nums:
            logger.warning("No test files found in directory")
            return 0
        
        # Load ONLY the tests that were actually sent (not fill gaps)
        for test_num in sorted(test_nums):
            matching_file = self._find_test_file(test_num)
            
            if matching_file:
                logger.info(f"Loading test {test_num} from: {matching_file.name}")
                if self.load_test_file(matching_file, test_num):
                    loaded_count += 1
                    logger.info(f"Successfully loaded test {test_num}: {len(self.test_data.get(test_num, {}))} participants")
            else:
                logger.warning(f"Test {test_num} was detected but file not found (should not happen)")
        
        return loaded_count
    
    def _find_test_file(self, test_num: int) -> Optional[Path]:
        """Find the file matching a specific test number"""
        for f in sorted(self.input_dir.glob("*.xlsx")):
            if self._extract_test_number_from_file(f.name) == test_num:
                return f
        return None
    
    @staticmethod
    def _extract_test_number_from_file(filename: str) -> Optional[int]:
        """
        Extract test number from filename (matches _extract_test_number in telegram_bot)
        Supports: 'Test 1', 'test1', '1.xlsx', 'result_1', 'exam(1)', etc.
        """
        import re
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        # Try 1: Look for "Test N" or "test N" format first
        match = re.search(r'[Tt]est\s*(\d+)', name_without_ext)
        if match:
            return int(match.group(1))
        
        # Try 2: Look for any number in the filename
        match = re.search(r'(\d+)', name_without_ext)
        if match:
            return int(match.group(1))
        
        return None
        return loaded_count
    
    def consolidate_results(self) -> Dict:
        """
        Consolidate results from all tests into a single dataset dynamically
        
        Returns:
            Dict: Consolidated data {email: {name, test_1_score, test_2_score, ...}}
        """
        if not self.test_data:
            logger.warning("No test data loaded")
            return {}
        
        # Use Test 1 as base
        if 1 not in self.test_data:
            logger.error("Test 1 data is required as the base")
            return {}
        
        logger.info(f"Starting consolidation with {len(self.test_data)} test datasets")
        for test_num in sorted(self.test_data.keys()):
            logger.info(f"  Test {test_num}: {len(self.test_data[test_num])} participants")
        
        consolidated = {}
        
        # Iterate through Test 1 participants ONLY (primary source)
        for email, data in self.test_data[1].items():
            consolidated[email] = {
                'name': data['name'],
                'test_1_score': data['score']
            }
            
            # Add scores from all other tests dynamically by matching email
            for test_num in sorted(self.test_data.keys()):
                if test_num != 1:
                    # Only add if email matches in that test (don't copy Test 1 score)
                    if email in self.test_data[test_num]:
                        score = self.test_data[test_num][email]['score']
                        consolidated[email][f'test_{test_num}_score'] = score
                        logger.debug(f"  {email}: Test {test_num} score = {score}")
                    else:
                        # Explicitly set as None if not found
                        consolidated[email][f'test_{test_num}_score'] = None
                        logger.debug(f"  {email}: Test {test_num} NOT FOUND (None)")
        
        # Sort by name
        consolidated = dict(sorted(consolidated.items(), 
                                  key=lambda x: x[1]['name'].lower()))
        
        logger.info(f"Consolidated {len(consolidated)} participants across {len(self.test_data)} tests")
        return consolidated
    
    def save_consolidated_file(self, consolidated_data: Dict, output_filename: str = "Consolidated_Results.xlsx") -> bool:
        """
        Save consolidated results to Excel file with color coding (dynamic columns)
        
        Args:
            consolidated_data (Dict): Consolidated results
            output_filename (str): Output filename
            
        Returns:
            bool: True if successful
        """
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Results"
            
            # Get number of tests from data keys
            test_nums = []
            if consolidated_data:
                first_record = next(iter(consolidated_data.values()))
                for key in first_record:
                    if key.startswith('test_') and key.endswith('_score'):
                        test_num = int(key.split('_')[1])
                        test_nums.append(test_num)
                test_nums = sorted(test_nums)
            
            # Create headers dynamically
            headers = ['Full Name', 'Email'] + [f'Test {num} Score' for num in test_nums]
            ws.append(headers)
            
            # Format header row
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Add data rows
            for email, data in consolidated_data.items():
                row = [data['name'], email] + [data.get(f'test_{num}_score') for num in test_nums]
                ws.append(row)
            
            # Apply color coding to test score columns
            for row_idx in range(2, len(consolidated_data) + 2):
                for col_offset, test_num in enumerate(test_nums):
                    col_idx = col_offset + 3  # Column C onwards (A=name, B=email)
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.fill = get_fill_for_test(test_num)
                    cell.alignment = Alignment(horizontal='center')
            
            # Adjust column widths
            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 30
            for col_offset in range(len(test_nums)):
                col_letter = get_column_letter(col_offset + 3)
                ws.column_dimensions[col_letter].width = 15
            
            output_path = self.output_dir / output_filename
            wb.save(output_path)
            logger.info(f"Saved consolidated results to {output_path} ({len(test_nums)} tests)")
            return True
            
        except Exception as e:
            logger.error(f"Error saving consolidated file: {str(e)}")
            return False
    
    def save_as_pdf(self, consolidated_data: Dict, output_filename: str = "Consolidated_Results.pdf") -> bool:
        """
        Save consolidated results to PDF file (dynamic columns)
        
        Args:
            consolidated_data (Dict): Consolidated results
            output_filename (str): Output filename
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Saving results as PDF: {output_filename}")
            
            # Get test numbers
            test_nums = []
            if consolidated_data:
                first_record = next(iter(consolidated_data.values()))
                for key in first_record:
                    if key.startswith('test_') and key.endswith('_score'):
                        test_num = int(key.split('_')[1])
                        test_nums.append(test_num)
                test_nums = sorted(test_nums)
            
            # Prepare data for table
            data = [['Full Name', 'Email'] + [f'Test {num}' for num in test_nums]]
            
            for email, record in consolidated_data.items():
                row = [
                    record['name'],
                    email
                ] + [str(record.get(f'test_{num}_score') or '') for num in test_nums]
                data.append(row)
            
            # Create PDF
            output_path = self.output_dir / output_filename
            doc = SimpleDocTemplate(str(output_path), pagesize=letter, topMargin=0.5*inch)
            
            # Calculate column widths dynamically
            col_widths = [1.8*inch, 2.2*inch] + [0.9*inch] * len(test_nums)
            table = Table(data, colWidths=col_widths)
            
            # Style table
            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]
            
            # Add color backgrounds to test score columns dynamically
            for row_idx in range(1, len(data)):
                for col_offset, test_num in enumerate(test_nums):
                    col_idx = col_offset + 2  # Starting from column C
                    color_hex = TEST_COLORS.get(test_num, {}).get('rgb', 'FFFFFF')
                    rgb = colors.HexColor(f'#{color_hex}')
                    style_commands.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), rgb))
            
            table.setStyle(TableStyle(style_commands))
            
            # Build PDF
            elements = [table]
            doc.build(elements)
            
            logger.info(f"Saved PDF results to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving PDF file: {str(e)}")
            return False
    
    def save_as_docx(self, consolidated_data: Dict, output_filename: str = "Consolidated_Results.docx") -> bool:
        """
        Save consolidated results to DOCX file (dynamic columns)
        
        Args:
            consolidated_data (Dict): Consolidated results
            output_filename (str): Output filename
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Saving results as DOCX: {output_filename}")
            
            # Get test numbers
            test_nums = []
            if consolidated_data:
                first_record = next(iter(consolidated_data.values()))
                for key in first_record:
                    if key.startswith('test_') and key.endswith('_score'):
                        test_num = int(key.split('_')[1])
                        test_nums.append(test_num)
                test_nums = sorted(test_nums)
            
            # Create document
            doc = Document()
            doc.add_heading('Consolidated Test Results', 0)
            
            # Add summary
            doc.add_paragraph(f'Total Participants: {len(consolidated_data)}')
            doc.add_paragraph(f'Tests Included: {len(test_nums)}')
            doc.add_paragraph('')
            
            # Create table with dynamic columns
            num_cols = len(test_nums) + 2  # Name + Email + Tests
            table = doc.add_table(rows=1, cols=num_cols)
            table.style = 'Light Grid Accent 1'
            
            # Add header row
            header_cells = table.rows[0].cells
            headers = ['Full Name', 'Email'] + [f'Test {num}' for num in test_nums]
            
            for idx, header_text in enumerate(headers):
                header_cells[idx].text = header_text
                # Style header
                paragraph = header_cells[idx].paragraphs[0]
                paragraph.runs[0].font.bold = True
            
            # Add data rows
            for email, record in consolidated_data.items():
                row_cells = table.add_row().cells
                row_cells[0].text = record['name']
                row_cells[1].text = email
                
                for col_offset, test_num in enumerate(test_nums):
                    row_cells[col_offset + 2].text = str(record.get(f'test_{test_num}_score') or '')
                
                # Center align score columns
                for col_idx in range(2, 2 + len(test_nums)):
                    for paragraph in row_cells[col_idx].paragraphs:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Save document
            output_path = self.output_dir / output_filename
            doc.save(output_path)
            
            logger.info(f"Saved DOCX results to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving DOCX file: {str(e)}")
            return False
