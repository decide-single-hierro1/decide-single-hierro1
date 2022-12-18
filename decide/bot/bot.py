import discord
from decide import settings
import os
import requests
import json
import threading
from discord.ext import commands
import asyncio
import base64
#from base import mods
#from django.http import Http404



 
    
client = discord.Client(intents=discord.Intents.all())
    
async def get_voting():
    response = requests.get("http://localhost:8000/visualizer/votes/")
    json_data = json.loads(response.txt)
    return json_data

@client.event
async def on_ready():
        print('We have logged in as {0.user}'.format(client))

@client.event

async def on_message( message):


        if message.author == client.user:
            return
	if message.content.startswith("$help"):

	    await client.channel.send("Las opciones son: $votes, $started, $list")
        if message.content.startswith("$votes"):
            await  message.channel.send("Indique el ID de la votación")
            try:
                wt =  await client.wait_for('message', timeout=10)
               
            except asyncio.TimeoutError:
                return await  message.channel.send("Lo siento pero se fue de tiempo")
            response = requests.get("http://localhost:8000/visualizer/votes/"+wt.content)

            if response.text=="0":
                await message.channel.send("Lo siento pero esa votación aun no está cerrada")
            else:  
                await message.channel.send(response.text)
        elif message.content.startswith("$list"):
           
            response = requests.get("http://localhost:8000/visualizer/list")

            if response.text=="0":
                await message.channel.send("Lo siento pero no hay votos")
            else:  
                await message.channel.send(response.text)
        elif message.content.startswith("$started"):
           
            response = requests.get("http://localhost:8000/visualizer/started")

            if response.text=="0":
                await message.channel.send("Lo siento pero no hay ninguna votación empezada")
            else:  
                await message.channel.send(response.text)

        elif message.content.startswith("$finished"):

            response = requests.get("http://localhost:8000/visualizer/finished")

            if response.text=="0":
                await message.channel.send("Lo siento pero no hay votaciones acabadas")
            else:
                await message.channel.send(response.text)
def init():
        
	client.run((settings.DISCORD_KEY).replace(':',''))

