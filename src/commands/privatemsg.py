import logging
import os
import re
import sys

import discord

import util
import resources


@util.listenerfinder.register
class Admin(util.Listener):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('admincmd')

    def is_triggered_private_message(self, msg: discord.Message):
        return self.registry.is_admin(msg.author)

    async def on_private_message(self, msg: discord.Message):
        if re.match(r'restart', msg.content):
            await self.client.send_message(msg.channel, 'Restarting now...')
            await self.client.logout()
            os.execl(sys.executable, sys.executable, *sys.argv)

        elif re.match(r'shutdown', msg.content):
            await self.client.send_message(msg.channel, 'Shutting down...')
            await self.client.logout()
            sys.exit(0)

    def is_triggered_message(self, msg: discord.Message):
        return self.registry.is_admin(msg.author) and re.search(r'mute', msg.content)

    async def on_message(self, msg: discord.Message):
        if re.match(r'!mute', msg.content):
            for user in msg.mentions:
                await self.client.send_message(msg.channel, '%s has been banned from using this bot!' % user.mention)
                self.registry.muted.append(user)
                self.logger.debug('Added %s to banned, current list %s', user.name, self.registry.muted)
        elif re.match(r'!unmute', msg.content):
            for user in msg.mentions:
                await self.client.send_message(msg.channel, '%s is now allowed to use this bot!' % user.mention)
                self.registry.muted.remove(user)
                self.logger.debug('Removed %s from banned, current list: %s', user.name, self.registry.muted)


@util.listenerfinder.register
class Help(util.Listener):
    def is_triggered_private_message(self, msg: discord.Message):
        return re.match(r'help', msg.content)

    async def on_private_message(self, msg: discord.Message):
        categories = {}
        for c in self.registry.commands:
            print(c)
            help = c.get_help(msg)
            if help is not None:
                cat = help.category
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(help)

        output = '__**Available commands:**__\n\n'
        for cat, helps in sorted(categories.items()):
            output += '**{}**\n'.format(cat)
            for h in helps:
                output += '`{title}` {desc}\n'.format(title=h.title, desc=h.desc)
                output += '\n'
        await self.client.send_message(msg.channel, output)

    def get_help(self, msg):
        return util.Help('Private Message', 'help', 'Display this message')
