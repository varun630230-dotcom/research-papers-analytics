"""
Run All Phase Tests Across the Entire System
"""
import subprocess
import sys

scripts = [
    "backend/test_phase1.py",
    "backend/test_phase2.py",
    "backend/test_phase3.py",
    "backend/test_phase4.py",
    "backend/test_phase5.py",
    "backend/test_phase6.py",
    "backend/test_phase7.py",
    "backend/test_phase8.py",
    "backend/test_phase9.py",
    "backend/test_phase10.py",
    "backend/test_phase11.py",
    "backend/test_phase13.py",
]

total_failed = 0
for s in scripts:
    print(f"\n--- Running {s} ---")
    res = subprocess.run([sys.executable, s])
    if res.returncode != 0:
        print(f"FAILED: {s}")
        total_failed += 1
    else:
        print(f"PASSED: {s}")

print("\n" + "=" * 60)
if total_failed == 0:
    print("ALL PHASE TESTS PASSED SUCCESSFULLY! (100% Green)")
else:
    print(f"FAILURES DETECTED: {total_failed} test scripts failed.")
print("=" * 60)

sys.exit(total_failed)
