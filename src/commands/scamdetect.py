import asyncio
import logging
import re
import discord
import requests

import util

REDIRECT_LAYERS = 3
URL_REGEX = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
URL_REGEX2 = r'_^(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)(?:\.(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)*(?:\.(?:[a-z\x{00a1}-\x{ffff}]{2,})))(?::\d{2,5})?(?:/[^\s]*)?$_iuS'
UPDATE_PERIOD = 3600  # Every hour

log = logging.getLogger(__name__)
moderator_roles = ['moderator', 'unikrn staff', 'unikrn admin']


@util.listenerfinder.register
class URLModerator(util.Listener):
    def is_triggered_message(self, msg: discord.Message):
        should_delete = True
        if not re.match(URL_REGEX2, msg.content):
            log.warn("regular expression did not match")
            should_delete = False
        else:
            log.warn("regular expression matched")
            for role in msg.author.roles:
                log.warn("Role: " + role)
                if role.name.lower() in moderator_roles:
                    should_delete = False
        return should_delete

    async def on_message(self, msg: discord.Message):
        await self.client.delete_message(msg)
        notice = await self.client.send_message(msg.channel, '_A message from {} that contained a URL was deleted._'.format(msg.author.mention))
        await asyncio.sleep(15)
        await self.client.delete_message(notice)
        return


@util.listenerfinder.register
class AddressDeletor(util.Listener):
    def is_triggered_message(self, msg: discord.Message):
        if any((r.name.lower() in moderator_roles) for r in msg.author.roles):
            log.debug('message from person on crypto address whitelist, not moderating for addresses')
            return False
        if re.search(r'[0-9a-f]{38,45}', msg.content, flags=re.IGNORECASE):
            return True

    async def on_message(self, msg: discord.Message):
        log.info('detected potential scam address in message, deleting', msg.content)
        await self.client.delete_message(msg)
        notice = await self.client.send_message(msg.channel, '_A message from {} that contained an ethereum address was deleted._'.format(msg.author.mention))
        await asyncio.sleep(10)
        await self.client.delete_message(notice)
        return
