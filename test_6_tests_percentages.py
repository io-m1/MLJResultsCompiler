"""
Test Grade 6 Bonus System with 6 Tests and Final Scores in Percentages
Tests the bonus system with extended participation (6 tests) and validates percentage output
"""

import logging
import sys
from src.participation_bonus import ParticipationBonusCalculator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_six_tests_with_percentages():
    """Test bonus calculation with 6 tests and percentage display"""
    
    logger.info("=" * 60)
    logger.info("TEST: 6 Tests with Final Scores in Percentages")
    logger.info("=" * 60)
    
    # Test data with 6 test scores
    consolidated_data = {
        'student1@school.com': {
            'name': 'Alice (6 tests)',
            'email': 'student1@school.com',
            'test_1_score': 88.5,
            'test_2_score': 91.0,
            'test_3_score': 89.5,
            'test_4_score': 92.0,
            'test_5_score': 87.0,
            'test_6_score': 90.5,
        },
        'student2@school.com': {
            'name': 'Bob (6 tests)',
            'email': 'student2@school.com',
            'test_1_score': 75.0,
            'test_2_score': 78.5,
            'test_3_score': 76.0,
            'test_4_score': 79.5,
            'test_5_score': 77.0,
            'test_6_score': 80.0,
        },
        'student3@school.com': {
            'name': 'Charlie (6 tests)',
            'email': 'student3@school.com',
            'test_1_score': 95.0,
            'test_2_score': 97.5,
            'test_3_score': 96.0,
            'test_4_score': 98.0,
            'test_5_score': 94.5,
            'test_6_score': 99.0,
        }
    }
    
    test_nums = [1, 2, 3, 4, 5, 6]
    
    # Apply bonuses
    bonus_calc = ParticipationBonusCalculator()
    consolidated_data = bonus_calc.apply_bonuses_to_consolidated(
        consolidated_data, test_nums
    )
    
    # Display results with final scores as percentages
    logger.info("\n📊 FINAL RESULTS (WITH PERCENTAGES):\n")
    
    all_passed = True
    for email, participant_data in consolidated_data.items():
        name = participant_data.get('name', 'Unknown')
        bonus = participant_data.get('Grade_6_bonus', 0)
        final_avg = participant_data.get('final_average', 0)
        status = participant_data.get('status', 'UNKNOWN')
        
        # Format as percentages
        bonus_pct = f"{bonus:.1f}%" if bonus else "None"
        final_pct = f"{final_avg:.2f}%"
        
        logger.info(f"  👤 {name}")
        logger.info(f"     • Grade 6 Bonus: {bonus_pct}")
        logger.info(f"     • Final Score: {final_pct}")
        logger.info(f"     • Status: {status}")
        logger.info("")
        
        # Validate
        if status == "PASS" and final_avg < 50:
            logger.error(f"❌ ERROR: {name} marked PASS but score {final_pct} < 50%")
            all_passed = False
        elif status == "FAIL" and final_avg >= 50:
            logger.error(f"❌ ERROR: {name} marked FAIL but score {final_pct} >= 50%")
            all_passed = False
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("✅ All validations passed!")
    else:
        logger.error("❌ Some validations failed!")
    logger.info("=" * 60)
    
    return all_passed


def test_bonus_range_for_six_tests():
    """Verify 6 tests falls into correct bonus range (85-93%)"""
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Bonus Range for 6 Tests")
    logger.info("=" * 60)
    
    bonus_calc = ParticipationBonusCalculator()
    
    # Test high performer (6 tests, avg 93%)
    high_scores = [95, 93, 94, 92, 91, 96]
    bonus_high, info_high = bonus_calc.calculate_bonus_score(
        'high@school.com', 'High Performer', 
        {i+1: score for i, score in enumerate(high_scores)},
        [1, 2, 3, 4, 5, 6]
    )
    
    logger.info(f"\n🎯 High Performer (avg ~93.5%):")
    logger.info(f"   Bonus: {bonus_high}% (should be 85-93 range)")
    logger.info(f"   Info: {info_high.get('reason', 'N/A')}")
    
    # Test mid performer (6 tests, avg 78%)
    mid_scores = [80, 76, 79, 77, 78, 75]
    bonus_mid, info_mid = bonus_calc.calculate_bonus_score(
        'mid@school.com', 'Mid Performer',
        {i+1: score for i, score in enumerate(mid_scores)},
        [1, 2, 3, 4, 5, 6]
    )
    
    logger.info(f"\n🎯 Mid Performer (avg ~77.5%):")
    logger.info(f"   Bonus: {bonus_mid}% (should be 85-93 range)")
    logger.info(f"   Info: {info_mid.get('reason', 'N/A')}")
    
    # Validate ranges
    test_passed = True
    if bonus_high and not (85 <= bonus_high <= 93):
        logger.error(f"❌ High performer bonus {bonus_high}% not in 85-93 range")
        test_passed = False
    if bonus_mid and not (85 <= bonus_mid <= 93):
        logger.error(f"❌ Mid performer bonus {bonus_mid}% not in 85-93 range")
        test_passed = False
    
    logger.info("\n" + "=" * 60)
    if test_passed:
        logger.info("✅ Bonus range test passed!")
    else:
        logger.error("❌ Bonus range test failed!")
    logger.info("=" * 60)
    
    return test_passed


if __name__ == "__main__":
    logger.info("\n🚀 GRADE 6 BONUS SYSTEM: 6 TESTS & PERCENTAGE FORMAT\n")
    
    test1 = test_six_tests_with_percentages()
    test2 = test_bonus_range_for_six_tests()
    
    logger.info("\n" + "=" * 60)
    logger.info("FINAL RESULTS")
    logger.info("=" * 60)
    total = 2
    passed = sum([test1, test2])
    logger.info(f"Total Tests: {total} | Passed: {passed} | Failed: {total - passed}")
    logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
    logger.info("=" * 60)
    
    sys.exit(0 if passed == total else 1)
