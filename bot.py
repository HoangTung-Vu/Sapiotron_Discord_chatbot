import discord
import discord
#import response_bot
import os
from dotenv import load_dotenv
from engine import gen_text, Conversation
import time

load_dotenv(dotenv_path='.env')
key = 'KEY'
TOKEN = os.getenv(key = key)

intents = discord.Intents.default()
intents.message_content = True
file = open('log.txt', 'a+')
    

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

        if str(message.content.lower()) == "!start":
            history = []
            conversation = Conversation(id = message.channel.id,user_id= message.author.id , history = history)
            await message.channel.send(f"Multi-turn chat mode : on. Now you can chat with me in this channel, {message.author.name}")
            self.chats.append(conversation)
            self.channel_user.append([conversation.id, conversation.user_id])
            print(self.chats)
            print(self.channel_user)
            now = time.ctime()
            file.write(str(now) + str(self.chats)+ str(self.channel_user) +"\n")
            
        if str(message.content) == "!quit":
            await message.channel.send("Multi-turn chat mode : off")
            for conversation in self.chats:
                if conversation.id == message.channel.id and conversation.user_id == message.author.id:
                    self.chats.remove(conversation)
                    self.channel_user.remove([conversation.id, conversation.user_id])
                    del conversation
                    print(self.chats)
                    print(self.channel_user)
                    now = time.ctime()
                    file.write(str(now) + str(self.chats)+ str(self.channel_user)+ "\n")
                    
            
        for conversation in self.chats:
            if conversation.id == message.channel.id and conversation.user_id == message.author.id:
                try:
                    await message.channel.send(conversation.multi_turn_chat(str(message.content)))
                    return
                except Exception as e : 
                    await message.channel.send(e)
                    self.chats.remove(conversation)
                    history = []
                    conversation = Conversation(id = message.channel.id, user_id= message.author.id, history=history)
                    self.chats.append(conversation)

        if message.content.startswith("!") and [message.channel.id, message.author.id] not in self.channel_user:
            response = str(gen_text(mess = message.content[1:]))
            while len(response) > 2000:
                split_index = response.rfind('\n', 0, 1900)
                await message.channel.send(response[:split_index])
                response = response[split_index+1:]
            await message.channel.send(response)

    


        
client = MyClient(intents=intents)        
client.run(TOKEN)
