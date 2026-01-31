"""
MLJ Results Compiler - Main Entry Point
Automates consolidation of test results from SurveyHeart Excel files
"""

import logging
import sys
import argparse
from pathlib import Path
from excel_processor import ExcelProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_consolidation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main execution function"""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='MLJ Results Compiler - Consolidate test results from multiple XLSX files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py                    # Default: XLSX output
  python src/main.py --format pdf       # Generate PDF
  python src/main.py --format docx      # Generate DOCX
  python src/main.py -f xlsx            # Generate XLSX (explicit)
        """
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['xlsx', 'pdf', 'docx'],
        default='xlsx',
        help='Output format (default: xlsx)'
    )
    
    args = parser.parse_args()
    output_format = args.format.lower()
    
    # Define directories
    repo_root = Path(__file__).parent.parent
    input_dir = repo_root / "input"
    output_dir = repo_root / "output"
    
    logger.info("=" * 60)
    logger.info("MLJ Results Compiler Starting")
    logger.info(f"Output format: {output_format.upper()}")
    logger.info("=" * 60)
    
    # Validate directories exist
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return 1
    
    if not output_dir.exists():
        logger.error(f"Output directory not found: {output_dir}")
        return 1
    
    # Initialize processor
    processor = ExcelProcessor(str(input_dir), str(output_dir))
    
    # Load test files
    logger.info("Loading test files from input directory...")
    loaded_count = processor.load_all_tests(max_tests=5)
    
    if loaded_count == 0:
        logger.error("No test files found in input directory. Please place XLSX files there.")
        return 1
    
    logger.info(f"Successfully loaded {loaded_count} test file(s)")
    
    # Consolidate results
    logger.info("Consolidating results...")
    consolidated_data = processor.consolidate_results()
    
    if not consolidated_data:
        logger.error("Failed to consolidate results")
        return 1
    
    # Save in requested format
    logger.info(f"Saving consolidated results as {output_format.upper()}...")
    
    success = False
    output_file = None
    
    if output_format == 'xlsx':
        success = processor.save_consolidated_file(consolidated_data, "Consolidated_Results.xlsx")
        output_file = Path(output_dir) / "Consolidated_Results.xlsx"
    elif output_format == 'pdf':
        success = processor.save_as_pdf(consolidated_data, "Consolidated_Results.pdf")
        output_file = Path(output_dir) / "Consolidated_Results.pdf"
    elif output_format == 'docx':
        success = processor.save_as_docx(consolidated_data, "Consolidated_Results.docx")
        output_file = Path(output_dir) / "Consolidated_Results.docx"
    
    if success:
        logger.info("=" * 60)
        logger.info("Process completed successfully!")
        logger.info(f"Output file: {output_file}")
        logger.info("=" * 60)
        return 0
    else:
        logger.error(f"Failed to save results as {output_format.upper()}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
