#!/usr/bin/env python3
"""Test if Ollama LLM is working"""

from openai import OpenAI
from app.core.config import settings

def test_llm():
    try:
        print("=" * 60)
        print("Testing Ollama LLM Connection")
        print("=" * 60)
        
        # Initialize client
        print(f"\n1. Connecting to: {settings.OPENROUTER_BASE_URL}")
        print(f"   Model: {settings.LLM_MODEL}")
        
        client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        
        print("\n2. Sending test query...")
        
        # Simple test query
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, I am working!' if you can read this."}
            ],
            temperature=0.1
        )
        
        answer = response.choices[0].message.content
        
        print("\n3. LLM Response:")
        print(f"   {answer}")
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS: Ollama LLM is working!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR: Ollama LLM is NOT working!")
        print("=" * 60)
        print(f"\nError details: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Ollama is running: ollama serve")
        print("2. Check if model is installed: ollama list")
        print(f"3. Pull model if needed: ollama pull {settings.LLM_MODEL}")
        print("4. Check URL in .env: OPENROUTER_BASE_URL=http://localhost:11434/v1")
        
        return False

if __name__ == "__main__":
    test_llm()
