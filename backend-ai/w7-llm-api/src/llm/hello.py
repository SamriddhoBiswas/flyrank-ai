import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# We only run this if not in stub mode and if LLM_ENABLED is true. 
# But for hello.py, we just want to test if the client works when credentials are provided.
# Here we will just print what it would do.

print("Running hello.py...")
print(f"Base URL: {os.getenv('LLM_BASE_URL')}")
print(f"Model: {os.getenv('LLM_MODEL')}")
print("Skipping actual API call because we don't have a real OpenRouter API key yet.")
print("If you have a real key, update .env and uncomment the API call code.")

"""
# Uncomment to test real connectivity when you have a key
client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL"), 
    api_key=os.environ.get("LLM_API_KEY")
)

res = client.chat.completions.create(
    model=os.environ.get("LLM_MODEL"),
    messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
)
print(res.choices[0].message.content)
"""
