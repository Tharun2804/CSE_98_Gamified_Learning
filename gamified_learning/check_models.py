import google.generativeai as genai

# Configure with your API key
genai.configure(api_key="AIzaSyBHY2IVA8CiFYyzmO4PRnvBnO5_pMn2q1c")

print("Available Gemini Models:")
print("=" * 50)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"Model: {model.name}")
            print(f"Display Name: {model.display_name}")
            print("-" * 50)
except Exception as e:
    print(f"Error: {e}")
