import os

import data
import discord

from datetime import datetime

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Activity(name='!sid-time <name> <minutes>', type=discord.ActivityType.watching))

@client.event
async def on_message(message):
    #Check if user does not already have a time set
    if message.clean_content.startswith('!sid-time'):
        msg_list = message.clean_content.split(' ');
        if len(msg_list) == 3:
            target = msg_list[1]
            time = msg_list[2]

            try:
                int(time)
            except ValueError:
                await message.channel.send(f'You need to enter the number of minutes 😡')
            else:
                if not data.validate_name(target):
                    await message.channel.send(f'Cannot find name {target} 😢')
                elif not data.find_incomplete_event(data.find_user_id(target)):
                    data.add_event(target, time, message.channel.id)
                    await message.channel.send(f'Sid time for {target} activated. They have {str(time)} minutes to join. 🤖')
                else:
                    await message.channel.send(f"There is already an ongoing Sid Time event for {target} 😯")


@client.event
async def on_voice_state_update(member, before, after):
    if data.find_incomplete_event(member.id) and before.channel == None:
        ev = data.find_incomplete_event(member.id)
        data.complete_event(member.id)
        difference = datetime.now() - ev.get('time')
        text_channel_list = []
        for guild in client.guilds:
            for channel in guild.channels:
                if channel.type.name == 'text':
                    text_channel_list.append(channel)
        channel = list(filter(lambda x: ev.get('channel_id') == x.id, text_channel_list))[0]

        msg = ''
        if round(int(difference.total_seconds()/60) > int(ev.get('minutes'))):
            msg = 'Sid time wins again! 😢'
        elif round(int(difference.total_seconds()/60) == int(ev.get('minutes'))):
            msg = 'Just in time! ⌚'
        else:
            msg = 'Reverse Sid time is in effect ⏰'
        await channel.send(f"{member.display_name} took {str(round(difference.total_seconds()/60))} minutes to join when they said they would be {ev.get('minutes')} minutes. {msg}")

client.run(TOKEN)
