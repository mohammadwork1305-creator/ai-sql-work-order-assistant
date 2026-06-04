import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("API key loaded successfully.")
    print("Key starts with:", api_key[:7])
else:
    print("API key NOT found.")