import discord
import discord
#import response_bot
import os
from dotenv import load_dotenv
from engine import gen_text, Conversation
import time
from engine2 import gen_text_img, get_img
from google.ai.generativelanguage import Part, Content
from google.generativeai.types import content_types

load_dotenv(dotenv_path='.env')
key = 'KEY'
TOKEN = os.getenv(key = key)

intents = discord.Intents.default()
intents.message_content = True

    

class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.chats = []
        self.channel_user = []
    
    def start_multi__turn(self, message):
        history = []
        conversation = Conversation(id = message.channel.id,user_id= message.author.id , history = history)
        self.chats.append(conversation)
        self.channel_user.append([conversation.id, conversation.user_id])
        #print(self.chats)
        #print(self.channel_user)
        now = time.ctime()
        with open('log.txt', 'a+') as file:
            file.write(str(now)+ " " + str(self.channel_user) +"\n")
            file.close()
    
    def quit_multi_turn(self, message):
        for conversation in self.chats:
            if conversation.id == message.channel.id and conversation.user_id == message.author.id:
                self.chats.remove(conversation)
                self.channel_user.remove([conversation.id, conversation.user_id])
                del conversation
                #print(self.chats)
                #print(self.channel_user)
                now = time.ctime()
                with open('log.txt', 'a+') as file:
                    file.write(str(now)+ " " + str(self.channel_user) +"\n")
                    file.close()
                
    
    def try_get_img(self, message):
        img = get_img(message=message)
        if img == 0 : 
            return 0
        else:
            now = time.ctime()
            with open('log.txt', 'a+') as file:
                file.write(str(now) + " : image : "+ img)
            prompt = message.content[1:]
            response = gen_text_img(img_path=img, prompt=prompt)
            os.remove(img)
            return response
    
        
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(f"- {guild.name} (ID: {guild.id})")


    async def on_message(self,message):
        if message.author == self.user:
            return
    
        if message.content.startswith('$'):
            return
        if message.content.lower() == "!help":
            with open('help.txt', 'r') as File:
                instruction = File.read()
                await message.channel.send(instruction)
                return
            
        if str(message.content.lower()) == "!start":
            self.start_multi__turn(message = message)
            await message.channel.send(f"Multi-turn chat mode : on. Now <@{message.author.id}> can chat with me in this channel : {message.channel.name} ! ")
            return
            
        if str(message.content) == "!quit":
            self.quit_multi_turn(message = message)
            await message.channel.send(f"Multi-turn chat mode with <@{message.author.id}> in channel {message.channel.name} : off")
            return
            
        for conversation in self.chats:
            if conversation.id == message.channel.id and conversation.user_id == message.author.id:
                response = self.try_get_img(message)
                try:
                    if response == 0:
                        await message.reply(conversation.multi_turn_chat((message.content)), mention_author = False)
                    else :
                        if(message.content == ""):
                            req = content_types.to_content("an image sent")
                        else:
                            req = content_types.to_content(str(message.content))
                        req.role = "user"
                        res = content_types.to_content(str(response))
                        res.role = "model"
                        #print(req)
                        #print(res)
                        conversation.chat.history.append(req)
                        conversation.chat.history.append(res)
                        await message.reply(response, mention_author = False)
                    return
                except Exception as e : 
                    await message.reply(e, mention_author = False)
                    self.chats.remove(conversation)
                    history = []
                    conversation = Conversation(id = message.channel.id, user_id= message.author.id, history=history)
                    self.chats.append(conversation)

        if message.content.startswith("!") and [message.channel.id, message.author.id] not in self.channel_user:
            response = self.try_get_img(message= message)
            if response == 0:
                response = str(gen_text(mess = message.content[1:]))
            while len(response) > 2000:
                split_index = response.rfind('\n', 0, 1900)
                await message.channel.send(response[:split_index])
                response = response[split_index+1:]
            await message.channel.send(response)
                


client = MyClient(intents=intents)       
client.run(TOKEN)
