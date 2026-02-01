#!/usr/bin/env python3
"""
Participation Bonus Scoring Test
Tests Grade 6 bonus calculation system
Date: February 1, 2026
"""

import os
import sys
import logging
from pathlib import Path

# Force UTF-8 output
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from src.participation_bonus import ParticipationBonusCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ParticipationBonusTest:
    """Test participation bonus scoring"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.calculator = ParticipationBonusCalculator()
    
    def test_bonus_calculation(self):
        """Test 1: Bonus calculation for different participation levels"""
        logger.info("\n📋 Test 1: Bonus Calculation")
        try:
            # Test case 1: 5 tests (high participation)
            participant_scores_5 = {1: 85, 2: 88, 3: 92, 4: 86, 5: 90}
            bonus_5, info_5 = self.calculator.calculate_bonus_score(
                "student1@school.com",
                "Student One",
                participant_scores_5,
                [1, 2, 3, 4, 5]
            )
            assert bonus_5 is not None, "5 tests should have bonus"
            assert 85 <= bonus_5 <= 93, f"5-test bonus should be 85-93, got {bonus_5}"
            logger.info(f"  ✅ 5 tests: {bonus_5}% bonus")
            
            # Test case 2: 3 tests (fixed bonus)
            participant_scores_3 = {1: 75, 2: 80, 3: 78}
            bonus_3, info_3 = self.calculator.calculate_bonus_score(
                "student2@school.com",
                "Student Two",
                participant_scores_3,
                [1, 2, 3, 4, 5]
            )
            assert bonus_3 == 80, f"3 tests should have 80% bonus, got {bonus_3}"
            logger.info(f"  ✅ 3 tests: {bonus_3}% bonus (fixed)")
            
            # Test case 3: 2 tests (range based)
            participant_scores_2a = {1: 92, 2: 95}
            bonus_2a, info_2a = self.calculator.calculate_bonus_score(
                "student3@school.com",
                "Student Three (High)",
                participant_scores_2a,
                [1, 2, 3, 4, 5]
            )
            assert 70 <= bonus_2a <= 75, f"2-test bonus should be 70-75, got {bonus_2a}"
            logger.info(f"  ✅ 2 tests (high scores): {bonus_2a}% bonus")
            
            # Test case 4: 1 test (no bonus)
            participant_scores_1 = {1: 85}
            bonus_1, info_1 = self.calculator.calculate_bonus_score(
                "student4@school.com",
                "Student Four",
                participant_scores_1,
                [1, 2, 3, 4, 5]
            )
            assert bonus_1 is None, "1 test should have NO bonus"
            logger.info(f"  ✅ 1 test: No bonus")
            
            self.passed += 1
            logger.info("  ✅ Bonus calculation working correctly")
            return True
        except Exception as e:
            logger.error(f"  ❌ Test failed: {e}")
            self.failed += 1
            self.errors.append(f"Bonus Calculation: {e}")
            return False
    
    def test_consolidated_bonus_application(self):
        """Test 2: Apply bonuses to consolidated data"""
        logger.info("\n📋 Test 2: Consolidated Bonus Application")
        try:
            # Create sample consolidated data
            consolidated_data = {
                'student1@school.com': {
                    'name': 'Alice (5 tests)',
                    'test_1_score': 85,
                    'test_2_score': 88,
                    'test_3_score': 90,
                    'test_4_score': 87,
                    'test_5_score': 92
                },
                'student2@school.com': {
                    'name': 'Bob (3 tests)',
                    'test_1_score': 75,
                    'test_2_score': 78,
                    'test_3_score': 80,
                    'test_4_score': None,
                    'test_5_score': None
                },
                'student3@school.com': {
                    'name': 'Charlie (2 tests)',
                    'test_1_score': 72,
                    'test_2_score': 75,
                    'test_3_score': None,
                    'test_4_score': None,
                    'test_5_score': None
                }
            }
            
            # Apply bonuses
            result = self.calculator.apply_bonuses_to_consolidated(
                consolidated_data, [1, 2, 3, 4, 5]
            )
            
            # Verify bonuses
            alice = result['student1@school.com']
            bob = result['student2@school.com']
            charlie = result['student3@school.com']
            
            # Check Alice (5 tests)
            assert alice['Grade_6_bonus'] is not None, "Alice should have bonus"
            assert 85 <= alice['Grade_6_bonus'] <= 93, "Alice bonus out of range"
            assert alice['final_average'] > 0, "Alice should have final average"
            assert alice['status'] == 'PASS', "Alice should PASS"
            logger.info(f"  ✅ Alice: {alice['Grade_6_bonus']}% bonus, {alice['final_average']}% avg, {alice['status']}")
            
            # Check Bob (3 tests)
            assert bob['Grade_6_bonus'] == 80, "Bob should have 80% bonus"
            assert bob['final_average'] > 0, "Bob should have final average"
            assert bob['status'] == 'PASS', "Bob should PASS"
            logger.info(f"  ✅ Bob: {bob['Grade_6_bonus']}% bonus, {bob['final_average']}% avg, {bob['status']}")
            
            # Check Charlie (2 tests)
            assert charlie['Grade_6_bonus'] is not None, "Charlie should have bonus"
            assert 70 <= charlie['Grade_6_bonus'] <= 75, "Charlie bonus out of range"
            assert charlie['final_average'] > 0, "Charlie should have final average"
            logger.info(f"  ✅ Charlie: {charlie['Grade_6_bonus']}% bonus, {charlie['final_average']}% avg, {charlie['status']}")
            
            self.passed += 1
            logger.info("  ✅ Consolidated bonus application working correctly")
            return True
        except Exception as e:
            logger.error(f"  ❌ Test failed: {e}")
            self.failed += 1
            self.errors.append(f"Consolidated Bonus: {e}")
            return False
    
    def test_final_average_calculation(self):
        """Test 3: Final average calculation with pass/fail"""
        logger.info("\n📋 Test 3: Final Average & Pass/Fail")
        try:
            consolidated_data = {
                'highpass@school.com': {
                    'name': 'High Pass Student',
                    'test_1_score': 75,
                    'test_2_score': 80,
                    'test_3_score': 85
                },
                'lowfail@school.com': {
                    'name': 'Low Fail Student (1 test)',
                    'test_1_score': 35,
                    'test_2_score': None,
                    'test_3_score': None
                }
            }
            
            result = self.calculator.apply_bonuses_to_consolidated(
                consolidated_data, [1, 2, 3]
            )
            
            # Check High Pass Student
            high_pass = result['highpass@school.com']
            assert high_pass['final_average'] >= 50, "High pass should have >= 50%"
            assert high_pass['status'] == 'PASS', "High pass should PASS"
            logger.info(f"  ✅ High Pass: {high_pass['final_average']}% → {high_pass['status']}")
            
            # Check Low Fail Student (1 test, no bonus - will fail)
            low_fail = result['lowfail@school.com']
            assert low_fail['final_average'] < 50, "Low fail (1 test) should have < 50%"
            assert low_fail['status'] == 'FAIL', "Low fail (1 test) should FAIL"
            logger.info(f"  ✅ Low Fail (1 test only): {low_fail['final_average']}% → {low_fail['status']}")
            
            self.passed += 1
            logger.info("  ✅ Final average and pass/fail working correctly")
            return True
        except Exception as e:
            logger.error(f"  ❌ Test failed: {e}")
            self.failed += 1
            self.errors.append(f"Final Average: {e}")
            return False
    
    def test_performance_percentile(self):
        """Test 4: Performance percentile calculation"""
        logger.info("\n📋 Test 4: Performance Percentile")
        try:
            # High performer
            high_scores = [95, 93, 92, 94]
            high_percentile = self.calculator.calculate_previous_score_percentile(high_scores)
            assert high_percentile > 0.8, "High performer should have high percentile"
            logger.info(f"  ✅ High performer (avg 93.5%): percentile {high_percentile}")
            
            # Low performer
            low_scores = [45, 48, 42, 40]
            low_percentile = self.calculator.calculate_previous_score_percentile(low_scores)
            assert low_percentile < 0.4, "Low performer should have low percentile"
            logger.info(f"  ✅ Low performer (avg 43.75%): percentile {low_percentile}")
            
            # Mid performer
            mid_scores = [70, 75, 72, 68]
            mid_percentile = self.calculator.calculate_previous_score_percentile(mid_scores)
            assert 0.4 <= mid_percentile <= 0.7, "Mid performer should have mid percentile"
            logger.info(f"  ✅ Mid performer (avg 71.25%): percentile {mid_percentile}")
            
            self.passed += 1
            logger.info("  ✅ Performance percentile working correctly")
            return True
        except Exception as e:
            logger.error(f"  ❌ Test failed: {e}")
            self.failed += 1
            self.errors.append(f"Percentile: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 60)
        logger.info("PARTICIPATION BONUS SCORING TEST SUITE")
        logger.info("=" * 60)
        logger.info(f"\n🚀 TESTING GRADE 6 BONUS SYSTEM\n")
        
        self.test_bonus_calculation()
        self.test_consolidated_bonus_application()
        self.test_final_average_calculation()
        self.test_performance_percentile()
        
        # Print summary
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total: {total} | Passed: {self.passed} | Failed: {self.failed}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        if self.errors:
            logger.error(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                logger.error(f"  - {error}")
        
        return self.passed, self.failed


def main():
    import asyncio
    tester = ParticipationBonusTest()
    passed, failed = asyncio.run(tester.run_all_tests())
    
    if failed > 0:
        logger.warning(f"\nSome tests failed.")
        sys.exit(1)
    else:
        logger.info(f"\n✅ All tests passed! Grade 6 bonus system is ready.")
        sys.exit(0)


if __name__ == "__main__":
    main()
