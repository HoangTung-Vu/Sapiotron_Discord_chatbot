import google.generativeai as genai
import re
from dotenv import load_dotenv
import os
from PIL import Image
import requests
import uuid
import shutil
import discord

load_dotenv(dotenv_path='.env')
key = 'GOOGLE_API_KEY2'
GOOGLE_API_KEY = os.getenv(key = key)
genai.configure(api_key=GOOGLE_API_KEY)
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)
    
model = genai.GenerativeModel('gemini-pro-vision')

def gen_text_img(img_path, prompt):
    img = Image.open(img_path)
    if prompt == "":
        response = model.generate_content(img)
        return str(response.text)
    response = model.generate_content([prompt, img])
    return str(response.text)

def get_img(message):
    try :
        url = message.attachments[0].url
        #print(url)
        if url.startswith("https://cdn.discordapp.com"):
            print("yes")
            r = requests.get(url, stream=True)
            image_name = "temp_img/" + str(uuid.uuid4()) + '.jpg'
            with open(image_name, 'wb') as out_file :
                print('Saving image: '+ image_name)
                shutil.copyfileobj(r.raw, out_file)
                out_file.close()
            return image_name
    except IndexError:
        return 0
    
    
if __name__ == '__main__':
    img = 'temp_img\\e706fa6a-103e-4b87-9e8c-a4e2d1bced5a.jpg'
    res = gen_text_img(img_path = img, prompt="")
    print(res)