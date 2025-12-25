"""
Experiment script to test AiderService integration.

This script demonstrates how to use the AiderService to analyze and edit code
using the aider AI pair programming tool.
"""

import os
import sys

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.app.service.aider_service import AiderService
from src.infrastructure.logger import get_logger


def test_aider_availability():
    """Test if aider is installed and available."""
    print("\n=== Testing Aider Availability ===")
    log = get_logger(__name__)
    service = AiderService(log)

    is_available = service.check_aider_available()
    if is_available:
        print("✓ Aider is installed and available")
    else:
        print("✗ Aider is not available. Install with: pip install aider-chat")
    return is_available


def test_repo_map():
    """Test getting repository map from aider."""
    print("\n=== Testing Repository Map ===")
    log = get_logger(__name__)
    service = AiderService(log)

    repo_map = service.get_repo_map()
    print("Repository Map:")
    print(repo_map[:500])  # Print first 500 chars
    print("...")


def test_code_analysis():
    """Test analyzing code with aider."""
    print("\n=== Testing Code Analysis ===")

    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ OPENAI_API_KEY not set. Skipping analysis test.")
        return

    log = get_logger(__name__)
    service = AiderService(log)

    # Analyze a simple file
    test_file = "src/app/service/aider_service.py"
    if not os.path.exists(test_file):
        print(f"Test file {test_file} not found. Skipping.")
        return

    prompt = "Summarize the main functionality of this service in 2-3 sentences."

    print(f"Analyzing {test_file}...")
    result = service.analyze_code([test_file], prompt)
    print("\nAnalysis Result:")
    print(result)


def test_simple_analysis():
    """Test a very simple analysis that doesn't require actual aider execution."""
    print("\n=== Testing Simple Analysis (Dry Run) ===")
    log = get_logger(__name__)
    service = AiderService(log)

    # Just test the service initialization
    print(f"Service initialized with model: {service.model}")
    print(f"API key configured: {'Yes' if service.api_key else 'No'}")


def main():
    """Run all experiments."""
    print("=" * 60)
    print("Aider Service Integration Tests")
    print("=" * 60)

    # Test 1: Check availability
    is_available = test_aider_availability()

    # Test 2: Simple analysis (doesn't require aider)
    test_simple_analysis()

    if is_available:
        # Test 3: Get repo map (doesn't require API key)
        try:
            test_repo_map()
        except Exception as e:
            print(f"Repo map test failed: {e}")

        # Test 4: Code analysis (requires API key)
        try:
            test_code_analysis()
        except Exception as e:
            print(f"Code analysis test failed: {e}")
    else:
        print("\n⚠ Aider not available. Install with: poetry add aider-chat")

    print("\n" + "=" * 60)
    print("Experiments completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
