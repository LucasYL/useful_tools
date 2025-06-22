#!/usr/bin/env python3
"""
Test script for OpenRouter API connection and model availability
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter_api():
    """Test OpenRouter API connection and model availability"""
    
    # Check if API key is available
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ OPENROUTER_API_KEY not found in environment variables")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Initialize OpenRouter client
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        print("✓ OpenRouter client initialized")
    except Exception as e:
        print(f"✗ Failed to initialize OpenRouter client: {e}")
        return False
    
    # Test models to check
    models_to_test = [
        "anthropic/claude-3.7-sonnet",  # Old model
        "anthropic/claude-sonnet-4",    # New model
        "anthropic/claude-3-sonnet-20240229",  # Alternative
        "anthropic/claude-3-5-sonnet-20241022",  # Latest Claude 3.5
    ]
    
    for model in models_to_test:
        print(f"\n--- Testing model: {model} ---")
        
        try:
            # Simple test message
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, this is a test!' in exactly 5 words."}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            # Check response structure
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
                print(f"✓ SUCCESS: Model responded with: '{content}'")
                print(f"  Response type: {type(response)}")
                print(f"  Choices count: {len(response.choices)}")
                print(f"  Message content type: {type(content)}")
            else:
                print(f"✗ FAILED: Invalid response structure")
                print(f"  Response: {response}")
                
        except Exception as e:
            print(f"✗ FAILED: {e}")
            # Check if it's a model availability issue
            if "not found" in str(e).lower() or "invalid" in str(e).lower():
                print(f"  → Model '{model}' may not be available")
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                print(f"  → Rate limit or quota issue")
            elif "auth" in str(e).lower():
                print(f"  → Authentication issue")
    
    return True

def test_api_response_structure():
    """Test the specific response structure that main.py expects"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("✗ Cannot test response structure without API key")
        return
    
    print(f"\n{'='*60}")
    print("Testing API Response Structure")
    print(f"{'='*60}")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    # Test with a working model
    test_model = "anthropic/claude-3-5-sonnet-20241022"  # Known working model
    
    try:
        response = client.chat.completions.create(
            model=test_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Respond with exactly: 'Test successful'"}
            ],
            max_tokens=10,
            temperature=0
        )
        
        print(f"✓ API call successful")
        print(f"  Response object: {type(response)}")
        print(f"  Has choices: {hasattr(response, 'choices')}")
        
        if hasattr(response, 'choices'):
            print(f"  Choices length: {len(response.choices)}")
            if len(response.choices) > 0:
                choice = response.choices[0]
                print(f"  First choice type: {type(choice)}")
                print(f"  Has message: {hasattr(choice, 'message')}")
                
                if hasattr(choice, 'message'):
                    message = choice.message
                    print(f"  Message type: {type(message)}")
                    print(f"  Has content: {hasattr(message, 'content')}")
                    
                    if hasattr(message, 'content'):
                        content = message.content
                        print(f"  Content: '{content}'")
                        print(f"  Content type: {type(content)}")
                        
                        # This is the line that might be failing in main.py
                        try:
                            # Simulate the access pattern from main.py
                            test_access = response.choices[0].message.content
                            print(f"✓ Access pattern works: '{test_access}'")
                        except Exception as access_error:
                            print(f"✗ Access pattern failed: {access_error}")
                    else:
                        print(f"✗ Message has no content attribute")
                else:
                    print(f"✗ Choice has no message attribute")
            else:
                print(f"✗ Choices list is empty")
        else:
            print(f"✗ Response has no choices attribute")
            
    except Exception as e:
        print(f"✗ API call failed: {e}")

if __name__ == "__main__":
    print("Starting OpenRouter API tests...")
    test_openrouter_api()
    test_api_response_structure()
    print("\nTest completed!") 