import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-pro")


def query(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text
