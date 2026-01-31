"""
Color Configuration for Test Results
Maps each test number to its corresponding color code for Excel formatting
"""

from openpyxl.styles import PatternFill

# Color definitions for each test
TEST_COLORS = {
    1: {
        'name': 'White',
        'rgb': 'FFFFFF',
        'fill': PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
    },
    2: {
        'name': 'Sky Blue',
        'rgb': '87CEEB',
        'fill': PatternFill(start_color='87CEEB', end_color='87CEEB', fill_type='solid')
    },
    3: {
        'name': 'Yellow',
        'rgb': 'FFFF00',
        'fill': PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
    },
    4: {
        'name': 'Army Green',
        'rgb': '556B2F',
        'fill': PatternFill(start_color='556B2F', end_color='556B2F', fill_type='solid')
    },
    5: {
        'name': 'Red',
        'rgb': 'FF0000',
        'fill': PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
    }
}

def get_fill_for_test(test_number):
    """
    Get the PatternFill object for a given test number
    
    Args:
        test_number (int): Test number (1-5)
        
    Returns:
        PatternFill: The color fill object for that test
    """
    if test_number not in TEST_COLORS:
        raise ValueError(f"Invalid test number: {test_number}. Must be 1-5")
    return TEST_COLORS[test_number]['fill']

def get_color_name(test_number):
    """Get the name of the color for a test"""
    if test_number not in TEST_COLORS:
        raise ValueError(f"Invalid test number: {test_number}. Must be 1-5")
    return TEST_COLORS[test_number]['name']
