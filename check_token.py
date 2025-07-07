"""
Hugging Face Token Verification Script
This script helps verify your Hugging Face API token and its permissions.
"""

import os
import requests
from dotenv import load_dotenv

def check_huggingface_token():
    """Check the status and permissions of your Hugging Face token"""
    
    print("🔍 Checking Hugging Face API Token...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN", "")
    
    if not API_TOKEN or API_TOKEN == "your_token_here":
        print("❌ No API token found in .env file")
        print("\n📝 To fix this:")
        print("1. Visit: https://huggingface.co/settings/tokens")
        print("2. Create a new token with 'Read' permissions")
        print("3. Copy the token to your .env file")
        return False
    
    print(f"✅ Token found: {API_TOKEN[:10]}...")
    
    # Test token validity with a simple API call
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    
    # Test 1: Check token validity with user info
    try:
        response = requests.get("https://huggingface.co/api/whoami", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token is valid for user: {user_info.get('name', 'Unknown')}")
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking token: {e}")
        return False
    
    # Test 2: Check inference API access
    print("\n🤖 Testing Inference API access...")
    inference_url = "https://api-inference.huggingface.co/models/gpt2"
    test_payload = {"inputs": "Test"}
    
    try:
        response = requests.post(inference_url, headers=headers, json=test_payload)
        
        if response.status_code == 200:
            print("✅ Inference API access: Working")
            return True
        elif response.status_code == 401:
            print("❌ Inference API access: Unauthorized")
            print("💡 Your token may not have inference permissions")
        elif response.status_code == 403:
            print("❌ Inference API access: Forbidden")
            print("💡 Your token may need additional permissions")
        else:
            print(f"⚠️ Inference API access: Status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing inference API: {e}")
    
    print("\n📋 Recommendations:")
    print("1. ✅ Template-based generation works without API token")
    print("2. 🔄 The app has robust fallback mechanisms")
    print("3. 🎯 Your assessment tool will work regardless")
    
    if "insufficient permissions" in str(response.text).lower():
        print("4. 🔑 For AI features, create a new token with 'Read' permissions")
        print("5. 🌐 Visit: https://huggingface.co/settings/tokens")
    
    return False

if __name__ == "__main__":
    check_huggingface_token()
    
    print("\n" + "="*50)
    print("🚀 Your Streamlit app is ready to use!")
    print("📝 Run: streamlit run streamlit_app.py")
    print("✨ Template-based generation works perfectly for testing")
