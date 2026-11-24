"""
ResearchGap AI - Run All Verified Test Suites
==============================================
Runs all 12 phase test suites across the system.
"""

import subprocess
import sys
import os

TEST_SCRIPTS = [
    "backend/tests/test_phase1.py",
    "backend/tests/test_phase2.py",
    "backend/tests/test_phase3.py",
    "backend/tests/test_phase4.py",
    "backend/tests/test_phase5.py",
    "backend/tests/test_phase6.py",
    "backend/tests/test_phase7.py",
    "backend/tests/test_phase8.py",
    "backend/tests/test_phase9.py",
    "backend/tests/test_phase10.py",
    "backend/tests/test_phase11.py",
    "backend/tests/test_phase13.py",
]

total_failed = 0
for script in TEST_SCRIPTS:
    print(f"\n--- Running {script} ---")
    res = subprocess.run([sys.executable, script])
    if res.returncode != 0:
        print(f"❌ FAILED: {script}")
        total_failed += 1
    else:
        print(f"✅ PASSED: {script}")

print("\n" + "=" * 60)
if total_failed == 0:
    print("ALL PHASE TESTS PASSED SUCCESSFULLY! (100% Green)")
else:
    print(f"FAILURES DETECTED: {total_failed} test scripts failed.")
print("=" * 60)

sys.exit(total_failed)
