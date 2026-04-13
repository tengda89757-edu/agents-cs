#!/usr/bin/env python3
"""
Reproducibility Verification Script
====================================
Runs all unit tests, checks prompt version consistency, and outputs a
reproducibility report JSON.
"""

import json
import os
import sys
import unittest
from datetime import datetime

# Ensure package root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def check_prompt_versions() -> dict:
    """Verify all prompt JSON files have the same version."""
    prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
    versions = {}
    for fname in os.listdir(prompts_dir):
        if fname.endswith(".json"):
            path = os.path.join(prompts_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            versions[fname] = data.get("version", "MISSING")
    unique_versions = set(versions.values())
    return {
        "versions": versions,
        "consistent": len(unique_versions) == 1,
        "expected_version": list(unique_versions)[0] if len(unique_versions) == 1 else None,
    }


def run_test_suite() -> dict:
    """Discover and run all tests under tests/."""
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.join(os.path.dirname(__file__), "..", "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success": result.wasSuccessful(),
    }


def main():
    report = {
        "timestamp": datetime.now().isoformat(),
        "prompt_version_check": check_prompt_versions(),
        "test_results": run_test_suite(),
    }
    report["overall_pass"] = (
        report["prompt_version_check"]["consistent"] and report["test_results"]["success"]
    )

    out_path = os.path.join(os.path.dirname(__file__), "..", "reproducibility_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    if report["overall_pass"]:
        print("✅ Reproducibility verification PASSED")
    else:
        print("❌ Reproducibility verification FAILED")
    print(f"Report written to: {out_path}")
    print("=" * 60)

    sys.exit(0 if report["overall_pass"] else 1)


if __name__ == "__main__":
    main()
