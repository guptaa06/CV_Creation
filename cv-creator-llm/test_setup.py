"""
Setup verification script for CV Creator LLM
Run this to verify your installation is correct
"""
import sys
import importlib

def test_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} (Need 3.9+)")
        return False

def test_imports():
    """Test if all required packages are installed"""
    packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pdfplumber",
        "docx",
        "reportlab",
        "requests",
        "jinja2",
    ]

    all_ok = True
    print("\n📦 Testing Package Imports:")

    for package in packages:
        try:
            if package == "docx":
                importlib.import_module("docx")
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Not installed")
            all_ok = False

    return all_ok

def test_ollama_connection():
    """Test connection to Ollama"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("\n✅ Ollama is running")

            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]

            print("\n🤖 Available Models:")
            for name in model_names:
                print(f"  • {name}")

            # Check required models
            print("\n📋 Required Models Check:")
            required = ["gemma:2b", "llama3.2-vision:11b"]
            all_present = True

            for model in required:
                if model in model_names:
                    print(f"  ✅ {model}")
                else:
                    print(f"  ❌ {model} - Not found (run: ollama pull {model})")
                    all_present = False

            return all_present
        else:
            print("\n❌ Ollama API returned error")
            return False

    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to Ollama")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"\n❌ Error checking Ollama: {e}")
        return False

def test_directories():
    """Check if required directories exist"""
    import os

    dirs = ["uploads", "outputs", "samples", "app", "app/templates", "app/static"]

    print("\n📁 Directory Structure:")
    all_ok = True

    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ - Missing")
            all_ok = False

    return all_ok

def test_config():
    """Test configuration loading"""
    try:
        from app.config import settings
        print("\n⚙️  Configuration:")
        print(f"  • App Name: {settings.APP_NAME}")
        print(f"  • Ollama URL: {settings.OLLAMA_BASE_URL}")
        print(f"  • Text Model: {settings.TEXT_MODEL}")
        print(f"  • Vision Model: {settings.VISION_MODEL}")
        print(f"  • Port: {settings.PORT}")
        return True
    except Exception as e:
        print(f"\n❌ Configuration Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CV Creator LLM - Setup Verification")
    print("=" * 60)

    results = {
        "Python Version": test_python_version(),
        "Package Imports": test_imports(),
        "Ollama Connection": test_ollama_connection(),
        "Directory Structure": test_directories(),
        "Configuration": test_config(),
    }

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All checks passed! You're ready to go!")
        print("\nNext steps:")
        print("  1. Run: python run.py")
        print("  2. Open: http://localhost:8000")
        print("  3. Start creating optimized resumes!")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Install packages: pip install -r requirements.txt")
        print("  • Start Ollama: ollama serve")
        print("  • Pull models: ollama pull gemma:2b")
        print("  • Pull models: ollama pull llama3.2-vision:11b")

    print()

if __name__ == "__main__":
    main()
