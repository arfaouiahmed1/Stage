# 🚀 Quick Setup Guide

## Option 1: Template-Based Generation (Recommended for Testing)
**✅ Ready to use immediately - No setup required!**

1. Run the app: `streamlit run streamlit_app.py`
2. Choose "Template-Based (Fast)" in the sidebar
3. Generate assessment and start testing

## Option 2: AI-Powered Generation (Optional)
**🤖 For advanced AI-generated questions**

### Step 1: Get Your Free Hugging Face Token
1. Visit: https://huggingface.co/settings/tokens
2. Create a free account if you don't have one
3. Click "New token"
4. Name it (e.g., "streamlit-app")
5. Choose "Read" permission
6. Copy the generated token

### Step 2: Configure Your Token
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open the `.env` file in your project directory
3. Replace the line:
   ```
   HUGGINGFACE_API_TOKEN=your_token_here
   ```
   With:
   ```
   HUGGINGFACE_API_TOKEN=hf_your_actual_token_here
   ```
3. Save the file

### Step 3: Restart the App
```bash
# Stop the current app (Ctrl+C in terminal)
# Then restart:
streamlit run streamlit_app.py
```

## ✅ Verification
- **Template-Based**: Should work immediately
- **AI-Powered**: Look for "✅ API token configured" in the sidebar

## 🐛 Troubleshooting

### "Invalid credentials" Error
- ❌ Token is missing or incorrect
- ✅ Get a new token from Hugging Face
- ✅ Update `.env` file and restart

### "Model Loading" Message  
- ⏳ AI model is starting up (can take 1-2 minutes)
- ✅ Try again in a moment or use template-based

### Connection Errors
- 🌐 Check your internet connection
- ✅ Template-based generation works offline

## 💡 Recommendations
- **For Testing**: Use template-based generation
- **For Demo**: Use AI-powered if you have the token
- **For Production**: Consider both as fallback options

## 📞 Need Help?
- Check the error messages in the app - they provide specific guidance
- Template-based generation always works as a fallback
- The app is designed to gracefully handle API issues
