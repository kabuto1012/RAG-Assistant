#!/usr/bin/env python3
"""
Test script to verify the RDR2-RAG-Assistant setup
"""
import os
import sys

def test_env_setup():
    """Test if environment variables are properly set up"""
    print("Testing environment setup...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✓ .env file found")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✓ python-dotenv loaded successfully")
        except ImportError:
            print("✗ python-dotenv not installed")
            return False
    else:
        print("⚠ .env file not found (copy from .env.example)")
    
    # Check API keys
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        print("✓ GEMINI_API_KEY is set")
    else:
        print("✗ GEMINI_API_KEY not set or using placeholder value")
        return False
    
    return True

def test_imports():
    """Test if required packages can be imported"""
    print("\nTesting package imports...")
    
    try:
        import google.generativeai as genai
        print("✓ google-generativeai imported")
    except ImportError as e:
        print(f"✗ google-generativeai: {e}")
        return False
    
    try:
        import chromadb
        print("✓ chromadb imported")
    except ImportError as e:
        print(f"✗ chromadb: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers imported")
    except ImportError as e:
        print(f"✗ sentence-transformers: {e}")
        return False
    
    try:
        import requests
        print("✓ requests imported")
    except ImportError as e:
        print(f"✗ requests: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4 imported")
    except ImportError as e:
        print(f"✗ beautifulsoup4: {e}")
        return False
    
    return True

def test_knowledge_base():
    """Test if knowledge base files exist"""
    print("\nTesting knowledge base...")
    
    info_dir = "RedDeadRemeption2/info"
    if os.path.exists(info_dir):
        print("✓ info directory found")
        txt_files = [f for f in os.listdir(info_dir) if f.endswith('.txt')]
        print(f"✓ Found {len(txt_files)} knowledge base files")
        return True
    else:
        print("✗ info directory not found")
        return False

def main():
    """Run all tests"""
    print("RDR2-RAG-Assistant Setup Test")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    if test_env_setup():
        tests_passed += 1
    
    if test_imports():
        tests_passed += 1
    
    if test_knowledge_base():
        tests_passed += 1
    
    print(f"\nResults: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ Setup is ready! You can now run the agents.")
    else:
        print("❌ Setup incomplete. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()