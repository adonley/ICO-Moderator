import asyncio
import discord
import util


@util.listenerfinder.register
class Timer(util.Listener):
    def __init__(self):
        super().__init__()
        self._timeout = 25.0 * 60.0
        self._announce_channels = ["unikoingold", "random", "crypto-security"]
        self._should_post = dict()
        for chan in self._announce_channels:
            self._should_post[chan] = True

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
        if msg.channel in self._announce_channels:
            self._should_post[msg.channel] = True

    def cancel(self):
        self._task.cancel()
