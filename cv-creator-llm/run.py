"""
Quick start script for CV Creator LLM
"""
import uvicorn
import sys
import subprocess

def check_ollama():
    """Check if Ollama is running and models are available"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = response.json().get("models", [])
        model_names = [m.get("name", "") for m in models]

        required_models = ["gemma:2b", "llama3.2-vision:11b"]
        missing = [m for m in required_models if m not in model_names]

        if missing:
            print(f"⚠️  Warning: Missing models: {', '.join(missing)}")
            print("Please run:")
            for model in missing:
                print(f"  ollama pull {model}")
            return False

        print("✅ Ollama is running with required models")
        return True

    except Exception as e:
        print(f"❌ Ollama is not running or not accessible: {e}")
        print("Please start Ollama first")
        return False

def main():
    """Main entry point"""
    print("🤖 CV Creator using LLMs")
    print("=" * 50)

    # Check Ollama
    if not check_ollama():
        print("\n⚠️  Starting anyway, but LLM features may not work")

    print("\n🚀 Starting FastAPI server...")
    print("📍 Access the app at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop\n")

    # Start uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
