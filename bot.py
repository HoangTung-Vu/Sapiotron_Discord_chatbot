import discord
import discord
#import response_bot
import os
from dotenv import load_dotenv
from engine import gen_text, Conversation
import time
from engine2 import gen_text_img, get_img

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
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')


    async def on_message(self,message):
        if message.author == self.user:
            return
    
        if message.content.startswith('#'):
            return
        if message.content.lower() == "!help":
            with open('help.txt', 'r') as File:
                instruction = File.read()
                await message.channel.send(instruction)
                return
            
        if str(message.content.lower()) == "!start":
            history = []
            conversation = Conversation(id = message.channel.id,user_id= message.author.id , history = history)
            await message.channel.send(f"Multi-turn chat mode : on. Now <@{message.author.id}> can chat with me in this channel : {message.channel.name} ! ")
            self.chats.append(conversation)
            self.channel_user.append([conversation.id, conversation.user_id])
            print(self.chats)
            print(self.channel_user)
            now = time.ctime()
            with open('log.txt', 'a+') as file:
                file.write(str(now)+ " " + str(self.channel_user) +"\n")
                file.close()
            
        if str(message.content) == "!quit":
            await message.channel.send(f"Multi-turn chat mode with <@{message.author.id}> in channel {message.channel.name} : off")
            for conversation in self.chats:
                if conversation.id == message.channel.id and conversation.user_id == message.author.id:
                    self.chats.remove(conversation)
                    self.channel_user.remove([conversation.id, conversation.user_id])
                    del conversation
                    print(self.chats)
                    print(self.channel_user)
                    now = time.ctime()
                    with open('log.txt', 'a+') as file:
                        file.write(str(now)+ " " + str(self.channel_user) +"\n")
                        file.close()
            
        for conversation in self.chats:
            if conversation.id == message.channel.id and conversation.user_id == message.author.id:
                try:
                    await message.channel.send(f'---------------<{message.author.name}>--------------- \n' + conversation.multi_turn_chat(str(message.content)))
                    return
                except Exception as e : 
                    await message.channel.send(e)
                    self.chats.remove(conversation)
                    history = []
                    conversation = Conversation(id = message.channel.id, user_id= message.author.id, history=history)
                    self.chats.append(conversation)

        if message.content.startswith("!") and [message.channel.id, message.author.id] not in self.channel_user:
            img = get_img(message=message)
            if img == 0:
                response = str(gen_text(mess = message.content[1:]))
                while len(response) > 2000:
                    split_index = response.rfind('\n', 0, 1900)
                    await message.channel.send(response[:split_index])
                    response = response[split_index+1:]
                await message.channel.send(response)
            else:
                #print("save : " + str(img))
                print(img)
                prompt = message.content[1:]
                response = gen_text_img(img_path=img, prompt=prompt)
                await message.channel.send(response)
                os.remove(img)


client = MyClient(intents=intents)       
client.run(TOKEN)
