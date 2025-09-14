from google import genai
from google.genai import types
from dotenv import load_dotenv
import os 
load_dotenv()
api_key = os.getenv("My_gemini_api_key")
client=genai.Client(api_key=api_key)
with open ("mango.jpg","rb") as f:
    image_bytes=f.read()
response=client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
      types.Part.from_bytes(
        data=image_bytes,
        mime_type='image/jpeg',
      ),
      'what of the calories of this food'
    ]
    )
config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking)
        )
    
    

print(response.text)
import os
print("Current working directory:", os.getcwd())
