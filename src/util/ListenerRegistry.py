import logging

import asyncio
import discord

from . import Listener


class ListenerRegistry():
    """
    A thing that automatically calls listener methods for you
    """

    def __init__(self, client: discord.Client, admins: list = list(), **cfg) -> object:
        """
        Create a ListenerRegistry
        :param client: the client to use
        :param admins: the list of admins to use, must be a list of ID's
        """
        self.commands = []
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.WARN)
        self.client = client
        self.admins = admins
        self.muted = []
        self.cfg = cfg

    def is_admin(self, user: discord.User):
        """
        Check if a user is an admin
        :param user: the user to check
        :return: is an admin or not?
        """
        return user.id in self.admins

    def is_muted(self, user: discord.User):
        """
        Check if a user is prevented from using emotes
        :param user: the user to check
        :return: is muted?
        """
        return user in self.muted

    async def on_pre_load(self):
        """
        Run this prior to starting the client
        """
        tasks = []
        for listener in self.commands:
            if listener.registry is not self:
                continue
            tasks.append(asyncio.get_event_loop().create_task(listener.on_pre_load()))
        await asyncio.gather(*tasks)

    async def on_start(self):
        """
        When the bot is first started
        """
        for listener in self.commands:
            if listener.registry is not self:  # Ensure that the listener is registered to me
                continue
            await listener.on_start()

    async def on_message(self, msg: discord.Message):
        """
        When a message is recieved
        :param msg: the message
        """

        if msg.author == self.client.user:  # Prevent a feedback loop
            return

        for listener in self.commands:

            if listener.registry is not self:  # Ensure that the listener is registered to me
                continue

            if listener.is_triggered_message(msg) and (listener.overrides_mute() or not self.is_muted(msg.author)):
                self.logger.debug('Triggered message: {}'.format(listener))
                await listener.on_message(msg)

            if msg.channel.is_private and listener.is_triggered_private_message(msg):
                self.logger.debug('Triggered private message: {}'.format(listener))
                await listener.on_private_message(msg)

    async def on_member_join(self, member):
        for l in self.commands:
            await l.on_member_join(member)

    def add_listener(self, *args):
        """
        Add a listener to the registry
        :param args: a list of the listeners
        """
        for l in args:
            self.commands.append(l)
            l.registry = self