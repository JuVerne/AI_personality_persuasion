#!/usr/bin/env python
"""
Setup Verification Script
Tests all components before running the experiment.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """Check if all required packages are installed."""
    print("\n" + "="*60)
    print("Checking Dependencies")
    print("="*60)
    
    required = ["openai", "dotenv"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def check_environment():
    """Check if environment is properly configured."""
    print("\n" + "="*60)
    print("Checking Environment")
    print("="*60)
    
    from utils import load_env_file
    
    # Load .env file
    load_env_file()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("✗ OPENAI_API_KEY not set")
        print("\nSetup instructions:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your API key: cp .env.example .env")
        print("  3. Edit .env and add your OpenAI API key")
        return False
    
    if not api_key.startswith("sk-"):
        print("⚠ API key doesn't start with 'sk-' (may be invalid)")
        return False
    
    print(f"✓ API key configured (sk-...{api_key[-6:]})")
    return True


def check_import_modules():
    """Check if all modules can be imported."""
    print("\n" + "="*60)
    print("Checking Module Imports")
    print("="*60)
    
    modules = [
        "message_generator",
        "personality_creator",
        "llm_interface",
        "results_manager",
        "experiment_runner",
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0


def check_directories():
    """Check if required directories exist."""
    print("\n" + "="*60)
    print("Checking Directories")
    print("="*60)
    
    dirs = ["src", "results"]
    
    for dir_name in dirs:
        if os.path.isdir(dir_name):
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ - MISSING")
            return False
    
    return True


def test_api_connection():
    """Test connection to OpenAI API."""
    print("\n" + "="*60)
    print("Testing API Connection")
    print("="*60)
    
    try:
        from llm_interface import LLMInterface
        
        llm = LLMInterface()
        print("Testing connection to OpenAI API...", end=" ")
        
        if llm.test_connection():
            print("✓ Connected!")
            return True
        else:
            print("✗ Connection test failed")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all checks."""
    print("\n█" * 60)
    print("AI PERSONALITY PERSUASION - SETUP VERIFICATION")
    print("█" * 60)
    
    results = {
        "Dependencies": check_dependencies(),
        "Environment": check_environment(),
        "Directories": check_directories(),
        "Module Imports": check_import_modules(),
        "API Connection": test_api_connection(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check}: {status}")
    
    print("\n" + "="*60)
    
    if all(results.values()):
        print("✓ All checks passed! You're ready to run the experiment.")
        print("\nNext steps:")
        print("  python main.py             # Run basic experiment")
        print("  python advanced_example.py # See more examples")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print("\nFor help, check QUICK_START.md or README.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
