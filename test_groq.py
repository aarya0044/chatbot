import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # Load environment variables from .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    response = client.chat.completions.create(
    model="llama-3.1-8b-instant" ,
    messages=[{"role": "user", "content": "Hello, test message"}],
    max_tokens=50
)
    print("Success! Response:", response.choices[0].message.content)
except Exception as e:
    print("Error:", e)