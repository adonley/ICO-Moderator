import asyncio
import logging
import re
import discord

import util

REDIRECT_LAYERS = 3
URL_REGEX = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
URL_REGEX2 = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,‌​3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s‌​()<>]+|(([^\s()<‌​>]+|(([^\s()<>]+‌​)))*))+(?:&#‌​40;([^\s()<>]+|((‌​;[^\s()<>]+)))*&‌​#41;|[^\s`!()[&#‌​93;{};:'".,<>?«»“”‘’‌​]))""", re.DOTALL)

log = logging.getLogger(__name__)
moderator_roles = ['moderator', 'unikrn staff', 'unikrn admin']
DELETE_TIME = 5


@util.listenerfinder.register
class URLModerator(util.Listener):
    def __init__(self):
        super().__init__()

    def is_triggered_message(self, msg: discord.Message):
        should_delete = True
        if not re.match(URL_REGEX2, msg.content) and not re.match(URL_REGEX, msg.content):
            should_delete = False
        else:
            for role in msg.author.roles:
                if role.name.lower() in moderator_roles:
                    should_delete = False
        return should_delete

    async def on_message(self, msg: discord.Message):
        await self.client.delete_message(msg)
        notice = await self.client.send_message(msg.channel, '_A message from {} that contained a URL was deleted._'.format(msg.author.mention))
        channels = self.client.get_all_channels()
        for channel in channels:
            if channel.name.lower() == 'godwatch':
                message = '_{} removed message: {}, from channel {} because it contained a link._'.format(msg.author.mention, msg.content, msg.channel.mention)
                await self.client.send_message(channel, message)
        await asyncio.sleep(DELETE_TIME)
        await self.client.delete_message(notice)
        return


@util.listenerfinder.register
class AddressDeletor(util.Listener):
    def __init__(self):
        super().__init__()

    def is_triggered_message(self, msg: discord.Message):
        if any((r.name.lower() in moderator_roles) for r in msg.author.roles):
            return False
        if re.search(r'[0-9a-f]{38,45}', msg.content, flags=re.IGNORECASE):
            return True

    async def on_message(self, msg: discord.Message):
        log.info('detected potential scam address in message, deleting', msg.content)
        await self.client.delete_message(msg)
        notice = await self.client.send_message(msg.channel, '_A message from {} that contained an ethereum address was deleted._'.format(msg.author.mention))
        channels = self.client.get_all_channels()
        for channel in channels:
            if channel.name.lower() == 'godwatch':
                '_{} removed message: {}, from channel {}._'.format(msg.author.mention, msg.content,
                                                                    msg.channel.mention)
                await self.client.send_message(channel, '_{} removed message: {}, from channel {} because it contained an Ethereum address._'.format(msg.author.mention, msg.content, msg.channel.mention))
        await asyncio.sleep(DELETE_TIME)
        await self.client.delete_message(notice)
        return
