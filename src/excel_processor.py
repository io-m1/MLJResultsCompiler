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

from validators import clean_name, clean_email, parse_score, validate_row_data
from color_config import get_fill_for_test, TEST_COLORS

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
    
    def load_all_tests(self, max_tests: int = 5) -> int:
        """
        Load all test files from input directory
        
        Args:
            max_tests (int): Maximum number of tests to load (1-5)
            
        Returns:
            int: Number of tests successfully loaded
        """
        loaded_count = 0
        
        for test_num in range(1, max_tests + 1):
            pattern = f"*[Tt]est*{test_num}*.xlsx"
            matching_files = list(self.input_dir.glob(pattern))
            
            if matching_files:
                if self.load_test_file(matching_files[0], test_num):
                    loaded_count += 1
            else:
                logger.info(f"No test {test_num} file found")
        
        return loaded_count
    
    def consolidate_results(self) -> Dict:
        """
        Consolidate results from all tests into a single dataset
        
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
        
        consolidated = {}
        
        # Iterate through Test 1 participants
        for email, data in self.test_data[1].items():
            consolidated[email] = {
                'name': data['name'],
                'test_1_score': data['score']
            }
            
            # Add scores from Tests 2-5
            for test_num in range(2, 6):
                if test_num in self.test_data and email in self.test_data[test_num]:
                    consolidated[email][f'test_{test_num}_score'] = self.test_data[test_num][email]['score']
                else:
                    consolidated[email][f'test_{test_num}_score'] = None
        
        # Sort by name
        consolidated = dict(sorted(consolidated.items(), 
                                  key=lambda x: x[1]['name'].lower()))
        
        logger.info(f"Consolidated {len(consolidated)} participants")
        return consolidated
    
    def save_consolidated_file(self, consolidated_data: Dict, output_filename: str = "Consolidated_Results.xlsx") -> bool:
        """
        Save consolidated results to Excel file with color coding
        
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
            
            # Create headers
            headers = ['Full Name', 'Email', 'Test 1 Score', 'Test 2 Score', 'Test 3 Score', 'Test 4 Score', 'Test 5 Score']
            ws.append(headers)
            
            # Format header row
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Add data rows
            for email, data in consolidated_data.items():
                row = [
                    data['name'],
                    email,
                    data['test_1_score'],
                    data.get('test_2_score'),
                    data.get('test_3_score'),
                    data.get('test_4_score'),
                    data.get('test_5_score')
                ]
                ws.append(row)
            
            # Apply color coding to test score columns
            for row_idx in range(2, len(consolidated_data) + 2):
                for test_num in range(1, 6):
                    col_idx = test_num + 2  # Column C onwards
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.fill = get_fill_for_test(test_num)
                    cell.alignment = Alignment(horizontal='center')
            
            # Adjust column widths
            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 30
            for col in ['C', 'D', 'E', 'F', 'G']:
                ws.column_dimensions[col].width = 15
            
            output_path = self.output_dir / output_filename
            wb.save(output_path)
            logger.info(f"Saved consolidated results to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving consolidated file: {str(e)}")
            return False
    
    def save_as_pdf(self, consolidated_data: Dict, output_filename: str = "Consolidated_Results.pdf") -> bool:
        """
        Save consolidated results to PDF file
        
        Args:
            consolidated_data (Dict): Consolidated results
            output_filename (str): Output filename
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Saving results as PDF: {output_filename}")
            
            # Prepare data for table
            data = [['Full Name', 'Email', 'Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5']]
            
            for email, record in consolidated_data.items():
                row = [
                    record['name'],
                    email,
                    str(record.get('test_1_score') or ''),
                    str(record.get('test_2_score') or ''),
                    str(record.get('test_3_score') or ''),
                    str(record.get('test_4_score') or ''),
                    str(record.get('test_5_score') or '')
                ]
                data.append(row)
            
            # Create PDF
            output_path = self.output_dir / output_filename
            doc = SimpleDocTemplate(str(output_path), pagesize=letter, topMargin=0.5*inch)
            
            # Create table
            col_widths = [1.8*inch, 2.2*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch]
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
            
            # Add color backgrounds to test score columns
            for row_idx in range(1, len(data)):
                for test_num in range(1, 6):
                    col_idx = test_num + 2  # Starting from column C
                    color_hex = TEST_COLORS[test_num]['rgb']
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
        Save consolidated results to DOCX file
        
        Args:
            consolidated_data (Dict): Consolidated results
            output_filename (str): Output filename
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Saving results as DOCX: {output_filename}")
            
            # Create document
            doc = Document()
            doc.add_heading('Consolidated Test Results', 0)
            
            # Add summary
            doc.add_paragraph(f'Total Participants: {len(consolidated_data)}')
            doc.add_paragraph('')
            
            # Create table
            table = doc.add_table(rows=1, cols=7)
            table.style = 'Light Grid Accent 1'
            
            # Add header row
            header_cells = table.rows[0].cells
            headers = ['Full Name', 'Email', 'Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5']
            
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
                row_cells[2].text = str(record.get('test_1_score') or '')
                row_cells[3].text = str(record.get('test_2_score') or '')
                row_cells[4].text = str(record.get('test_3_score') or '')
                row_cells[5].text = str(record.get('test_4_score') or '')
                row_cells[6].text = str(record.get('test_5_score') or '')
                
                # Center align score columns
                for col_idx in range(2, 7):
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
