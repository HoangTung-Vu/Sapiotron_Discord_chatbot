import google.generativeai as genai
import re
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')
key = 'GOOGLE_API_KEY'
GOOGLE_API_KEY = os.getenv(key = key)
genai.configure(api_key=GOOGLE_API_KEY)
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)
    
model = genai.GenerativeModel('gemini-1.0-pro-latest')

def gen_text(mess):
  res = model.generate_content(
      mess,
      generation_config=genai.types.GenerationConfig(
          candidate_count=1,
          max_output_tokens=2000,
          temperature=0.5
      )
  )
  # print(f"Response object: {res}")

  if not res.candidates:
    return "The model couldn't generate any content for this prompt."

  response = str(res.text)
  return response
  
# print(gen_text("a long passage on how bjt works"))

class Conversation:
  def __init__(self, id, history):
    self.history = history
    self.chat = model.start_chat(history=self.history)
    self.id = id
  
  def multi_turn_chat(self, mess):
    response =  self.chat.send_message(mess)
    return str(response.text)
  
  def reset(self):
    self.history = []
    self.chat = model.start_chat(history=self.history)
  
  
# conversation = Conversation()
# print(conversation.multi_turn_chat("Hello! My name is Tung"))
# print(conversation.history)
# print(conversation.multi_turn_chat("can you repeat what my name is"))


# conversation.reset()
# print(conversation.multi_turn_chat("Do you remember my name?"))

