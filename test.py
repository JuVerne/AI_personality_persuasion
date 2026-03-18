
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# API configuration
api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
model = os.getenv("LLM_MODEL")
  
# Make sure API key is set
if not api_key:
    raise ValueError(
        "No API key found. Please set OPENAI_API_KEY or LLM_API_KEY in your .env or environment."
    )

print("Using configuration:")
print(f"  model:    {model}")
print(f"  base_url: {base_url or '<default openai>'}")

# Start OpenAI client
client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
  
# Get response
chat_completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How tall is the Eiffel tower?"},
    ],
    max_tokens=60,
    )
  
# Print full response as JSON
print(chat_completion)