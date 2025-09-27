#!/usr/bin/env python3
"""
Test execution script for Go Postal SD backend.

This script provides various test execution options:
- Run all tests
- Run specific test categories
- Run with coverage reporting
- Run performance tests
- Run with different verbosity levels
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False


def run_all_tests():
    """Run all tests with coverage."""
    command = [
        "pytest", 
        "tests/", 
        "--cov=server", 
        "--cov-report=html", 
        "--cov-report=term-missing",
        "--cov-fail-under=100",
        "-v"
    ]
    return run_command(command, "All Tests with 100% Coverage")


def run_unit_tests():
    """Run unit tests only."""
    command = [
        "pytest", 
        "tests/unit/", 
        "-v", 
        "--tb=short"
    ]
    return run_command(command, "Unit Tests")


def run_integration_tests():
    """Run integration tests only."""
    command = [
        "pytest", 
        "tests/integration/", 
        "-v", 
        "--tb=short"
    ]
    return run_command(command, "Integration Tests")


def run_api_tests():
    """Run API tests only."""
    command = [
        "pytest", 
        "tests/integration/api/", 
        "-v", 
        "--tb=short"
    ]
    return run_command(command, "API Tests")


def run_performance_tests():
    """Run performance tests only."""
    command = [
        "pytest", 
        "tests/integration/test_performance.py", 
        "-v", 
        "--tb=short",
        "-m", "performance"
    ]
    return run_command(command, "Performance Tests")


def run_specific_test(test_path):
    """Run a specific test file or test function."""
    command = [
        "pytest", 
        test_path, 
        "-v", 
        "--tb=short"
    ]
    return run_command(command, f"Specific Test: {test_path}")


def run_coverage_report():
    """Generate coverage report only."""
    command = [
        "pytest", 
        "tests/", 
        "--cov=server", 
        "--cov-report=html", 
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--quiet"
    ]
    return run_command(command, "Coverage Report Generation")


def run_fast_tests():
    """Run fast tests only (exclude slow tests)."""
    command = [
        "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "-m", "not slow"
    ]
    return run_command(command, "Fast Tests Only")


def run_with_parallel():
    """Run tests in parallel."""
    try:
        import pytest_xdist
        command = [
            "pytest", 
            "tests/", 
            "-n", "auto", 
            "-v", 
            "--tb=short"
        ]
        return run_command(command, "Parallel Tests")
    except ImportError:
        print("❌ pytest-xdist not installed. Install with: pip install pytest-xdist")
        return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Run Go Postal SD backend tests")
    parser.add_argument(
        "test_type", 
        choices=[
            "all", "unit", "integration", "api", "performance", 
            "coverage", "fast", "parallel", "specific"
        ],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--test-path", 
        help="Specific test path (required for 'specific' test type)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    success = False
    
    if args.test_type == "all":
        success = run_all_tests()
    elif args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "api":
        success = run_api_tests()
    elif args.test_type == "performance":
        success = run_performance_tests()
    elif args.test_type == "coverage":
        success = run_coverage_report()
    elif args.test_type == "fast":
        success = run_fast_tests()
    elif args.test_type == "parallel":
        success = run_with_parallel()
    elif args.test_type == "specific":
        if not args.test_path:
            print("❌ --test-path is required for 'specific' test type")
            sys.exit(1)
        success = run_specific_test(args.test_path)
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
