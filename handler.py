import hangups
from hangups import hangouts_pb2
from hangups.hangouts_pb2 import ParticipantId

import asyncio
from text_2048 import run_game, save_games, load_games
import random
from collections import defaultdict
from datetime import datetime, tzinfo
import json
import math
# import sys

from utils import *


class Handler:

    keywords = {
        "testblackjack": "currently-online",

    }
    images = {
    }

    def __init__(self):
        load_games()
        self.commands = {
            "/help": self.help_,
            "/rename": self.rename,
            "/say": self.say,
            "/rickroll": self.rickroll,
            "/quit": self.quit_,
            "/reset": self.reset,
            "/id": self.id_,
            "/kick": self.kick,
            "/blackjack": self.kick,
        }
        self.cooldowns = defaultdict(dict)
        self.admins = [
            114207595761187114730,  # joseph
            106637925595968853122,  # chendi
            ]
        self.ignore = [105849946242372037157]
        random.seed(datetime.now())

        with open("data.json") as f:
            self.data = json.load(f)
    # blackjack
    
    async def blacjack(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return
        await conv.send_message(toSeg("Welcome To Blackjack"))
        
        
    
    # utility
    async def help_(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return

        f = open("text/help.txt", 'r')
        contents = f.read()
        await conv.send_message(toSeg(contents))
        f.close()

    async def rename(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return

        try:
            await conv.rename(event.text.split(' ', 1)[1])
        except:
            await conv.send_message(toSeg("Format: /rename {name}"))

    async def say(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return

        try:
            await conv.send_message(toSeg(event.text.split(' ', 1)[1]))
        except:
            await conv.send_message(toSeg("Format: /say {message}"))

    async def id_(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 10):
            return

        try:
            await conv.send_message(toSeg(user.id_[0]))
        except:
            await conv.send_message(toSeg(str("Something went wrong!")))

    async def kick(self, bot, event):
        user, conv = getUserConv(bot, event)
        arg1 = event.text.lower().split()[1]
        users = conv.users
        ids = []
        kick_users = []

        try:
            for user in users:
                if arg1 in user.full_name.lower():
                    kick_users.append(user)

            if not kick_users:
                await conv.send_message(toSeg("Nobody in this conversation goes by that name"))
                return
            # only reason i figured this out was because of hangupsbot, so thank you so much https://github.com/xmikos/hangupsbot/blob/master/hangupsbot/commands/conversations.py

            ids = [ParticipantId(gaia_id=user.id_.gaia_id, chat_id=conv.id_) for user in kick_users]

            for kick_id in ids:
                request = hangouts_pb2.RemoveUserRequest(
                    request_header=bot.client.get_request_header(),
                    participant_id=kick_id,
                    event_request_header=conv._get_event_request_header()
                )
                res = await bot.client.remove_user(request)
                conv.add_event(res.created_event)
        except:
            await conv.send_message(toSeg("Yeah don't use this command lol"))

    # fun
    async def rickroll(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 3):
            return

        try:
            await conv.send_message(toSeg("https://youtu.be/dQw4w9WgXcQ"))
        except:
            await conv.send_message(toSeg("Something went wrong!"))

  
    # config

    async def quit_(self, bot, event):
        user, conv = getUserConv(bot, event)
        if cooldown(self.cooldowns, user, event, 30):
            return

        if isIn(self.admins, user):
            await conv.send_message(toSeg("Saber out!"))
            save_games()
            await bot.client.disconnect()
        else:
            await conv.send_message(toSeg("bro wtf u can't use that"))

    async def reset(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            arg1 = '/' + event.text.lower().split()[1]
            if isIn(self.admins, user):
                if arg1 in self.cooldowns[user]:
                    self.cooldowns[user][arg1] = datetime.min.replace(tzinfo=None)
                else:
                    await conv.send_message(toSeg("Format: /reset {command}"))
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except:
            await conv.send_message(toSeg("Format: /reset {command}"))

    async def save(self, bot, event):
        user, conv = getUserConv(bot, event)

        try:
            if isIn(self.admins, user):
                with open("data.json", "w") as f:
                    json.dump(self.data, f)
                await conv.send_message(toSeg("Successfully saved!"))
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))
        except:
            await conv.send_message(toSeg("Something went wrong!"))

    async def sync(self, bot, event):
        user, conv = getUserConv(bot, event)
        key = event.text.lower().split()[1]
        value = event.text.lower().split(' ', 2)[2]

        if value.isdigit():
            value = int(value)

        try:
            if isIn(self.admins, user):
                for user in self.data["users"]:
                    self.data["users"][user][key] = value

                    with open("data.json", "w") as f:
                        json.dump(self.data, f)

                    await conv.send_message(toSeg("Synced all values!"))
                    return
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))

        except Exception as e:
            await conv.send_message(toSeg("Something went wrong!"))
            print(e)

    async def remove(self, bot, event):
        user, conv = getUserConv(bot, event)
        key = event.text.lower().split()[1]

        try:
            if isIn(self.admins, user):
                for user in self.data["users"]:
                    self.data["users"][user].pop(key, None)

                    with open("data.json", "w") as f:
                        json.dump(self.data, f)

                    await conv.send_message(toSeg("Removed key!"))
                    return
            else:
                await conv.send_message(toSeg("bro wtf u can't use that"))

        except Exception as e:
            await conv.send_message(toSeg("Something went wrong!"))
            print(e)
