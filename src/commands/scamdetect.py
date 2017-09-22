import asyncio
import logging
import re
import discord
import requests

import util

REDIRECT_LAYERS = 3
URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
URL_REGEX2 = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,‌​3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s‌​()<>]+|(([^\s()<‌​>]+|(([^\s()<>]+‌​)))*))+(?:&#‌​40;([^\s()<>]+|((‌​;[^\s()<>]+)))*&‌​#41;|[^\s`!()[&#‌​93;{};:'".,<>?«»“”‘’‌​]))""", re.DOTALL)
ANY_URL_REGEX = re.compile(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")
WEB_URL_REGEX = re.compile(r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|top|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")
IP_REGEX = re.compile(r"""[0-9]+(?:\.[0-9]+){3}:[0-9]+""")
STACKOVERFLOW_REGEX = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''')

ALLOWED_SITES = ["https://unikoingold.com/", "http://unikoingold.com/", "https://unikoingold.com", "http://unikoingold.com/",
                 "https://unikrn.com/", "https://unikrn.com", "https://tv.unikrn.com/", "https://tv.unikrn.com", "tv.unikrn.com",
                 "https://unikoingold.com/whitepaper"]

REGS = [URL_REGEX, URL_REGEX2, ANY_URL_REGEX, WEB_URL_REGEX, IP_REGEX, STACKOVERFLOW_REGEX]

log = logging.getLogger()
moderator_roles = ['moderator', 'unikrn staff', 'unikrn admin']
DELETE_TIME = 5


URL_SOURCE = 'https://raw.githubusercontent.com/MyEtherWallet/ethereum-lists/master/urls-darklist.json'
UPDATE_PERIOD = 3600  # Every hour





@util.listenerfinder.register
class BanBadNamesTask(util.ScheduledTask):
    bad_names = ["discord"]
    async def task(self):
        while True:
            for member in list(self.client.get_all_members()):
                for bad_name in BanBadNamesTask.bad_names:
                    if bad_name.lower() in member.display_name.lower():
                        await self.send_to_godwatch(member)
                        await self.client.ban(member, delete_message_days=1)
                    pass
            await asyncio.sleep(15.0)

    async def send_to_godwatch(self, member):
        for channel in self.client.get_all_channels():
            if channel.name.lower() == 'godwatch':
                message = '{} has a display name {} that\'s been matched with abuse. They\'ve been banned.'.format(
                    member.mention, member.display_name)
                await self.client.send_message(channel, message)


@util.listenerfinder.register
class GetUrlsTask(util.ScheduledTask):

    blacklist = []

    async def task(self):
        while True:
            log.info('updating url blacklist...')
            response = requests.get(URL_SOURCE)
            content = response.content.decode()
            GetUrlsTask.blacklist = re.findall(r'"id": ?"(.+)"', content)  # because it errors with proper json.loads...
            log.debug('updated blacklist: ', GetUrlsTask.blacklist)
            await asyncio.sleep(UPDATE_PERIOD)


@util.listenerfinder.register
class URLModerator(util.Listener):
    def __init__(self):
        super().__init__()

    def is_triggered_message(self, msg: discord.Message):
        should_delete = False

        for blacklist_url in GetUrlsTask.blacklist:
            if re.search(r'\b{}\b'.format(blacklist_url), msg.content, flags=re.IGNORECASE):
                should_delete = True

        for reg in REGS:
            should_delete = should_delete or re.match(reg, msg.content)

        split = msg.content.split(' ')
        for word in split:
            lower_word = word.lower()
            if lower_word.startswith("http:") or lower_word.startswith("https:") \
                    and lower_word not in ALLOWED_SITES:
                should_delete = True
            for extension in util.EXTENSTIONS:
                if lower_word.endswith("." + extension) \
                        and lower_word not in ALLOWED_SITES:
                    should_delete = True

        if msg.author and hasattr(msg.author, 'roles'):
            for role in msg.author.roles:
                if role.name.lower() in moderator_roles:
                    should_delete = False

        return should_delete

    async def on_message(self, msg: discord.Message):
        if not msg:
            return
        await self.client.delete_message(msg)
        notice = await self.client.send_message(msg.channel, '_A message from {} that contained a URL was deleted._'.format(msg.author.mention))
        channels = self.client.get_all_channels()
        for channel in channels:
            if channel.name.lower() == 'godwatch':
                message = '_{} removed message: {}, from channel {} because it contained a link._'.format(msg.author.mention, msg.content, msg.channel.mention)
                await self.client.send_message(channel, message)
        await asyncio.sleep(DELETE_TIME)
        if notice:
            await self.client.delete_message(notice)


@util.listenerfinder.register
class AddressDeletor(util.Listener):
    def is_triggered_message(self, msg: discord.Message):
        if any((r.name.lower() in moderator_roles) for r in msg.author.roles):
            return False
        if re.search(r'[0-9a-f]{38,45}', msg.content, flags=re.IGNORECASE):
            return True

    async def on_message(self, msg: discord.Message):
        if not msg:
            return
        await self.client.delete_message(msg)
        notice = await self.client.send_message(msg.channel, '_A message from {} that contained an ethereum address was deleted._'.format(msg.author.mention))
        channels = self.client.get_all_channels()
        for channel in channels:
            if channel.name.lower() == 'godwatch':
                '_{} removed message: {}, from channel {}._'.format(msg.author.mention, msg.content, msg.channel.mention)
                await self.client.send_message(channel, '_{} removed message: {}, from channel {} because it contained an Ethereum address._'.format(msg.author.mention, msg.content, msg.channel.mention))
        await asyncio.sleep(DELETE_TIME)
        if notice:
            await self.client.delete_message(notice)
        return


@util.listenerfinder.register
class AnnounceTimer(util.Listener):
    def __init__(self):
        super().__init__()
        self._timeout = 60.0 * 60.0 * 3
        self._announce_channels = ["unikoingold", "random", "crypto-security", "unikoin-gold-ama"]
        self._should_post = dict()
        for chan in self._announce_channels:
            self._should_post[chan] = True

    def is_triggered_message(self, msg: discord.Message):
            return True

    async def on_start(self):
        await self._job()

    async def _job(self):
        message = "Announcement: Do not send any ETH to an address provided to you in discord. The Unikrn team will not "
        message += "direct message you with an address to send funds or ask you to use any website. Please report any attempt to "
        message += "do so to a moderator. Thank you."
        for channel in self.client.get_all_channels():
            if channel.name in self._announce_channels:
                if self._should_post[channel.name]:
                    self._should_post[channel.name] = False
                    await self.client.send_message(channel, message)
        await asyncio.sleep(self._timeout)
        await self._job()

    async def on_message(self, msg: discord.Message):
        if msg.channel.name in self._announce_channels:
            self._should_post[msg.channel.name] = True