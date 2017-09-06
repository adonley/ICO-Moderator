"""
Start the bot from here
"""

import asyncio
import datetime
import getopt
import importlib
import json
import logging
import os
import sys
import time

import discord

import resources
import util

FORMAT = '%(asctime)s - %(name)s:%(module)s:%(lineno)d - %(levelname)s: %(message)s'

main_logger = logging.getLogger()


class IllegalArgumentException(Exception):
    pass


class UnicodeLogger(logging.getLoggerClass()):
    def log(self, level, msg, *args, **kwargs):
        try:
            super().log(level, str(msg).encode(), *args, **kwargs)
        except UnicodeEncodeError as e:
            pass


def main():
    global commandreg, client, loop, token

    try:
        args = get_args()
    except IllegalArgumentException:
        print('Not enough arguments. Usage:')
        print('python3 main.py -ttoken')
        print('python3 main.py cfgfilelocation')
        print('Put the token in one of the spots above.')
        print('loglevel is a standard Python logging level, where 10 is debug and 50 is error.')
        sys.exit(2)

    token = args['token']

    loop = asyncio.get_event_loop()

    logging_params = {
        'level': logging.WARN,
        'format': FORMAT
    }

    logging.setLoggerClass(UnicodeLogger)
    logging.basicConfig(**logging_params)
    formatter = logging.Formatter(fmt=FORMAT)

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    console.setLevel(logging.WARN)

    rootlogger = logging.getLogger()
    rootlogger.addHandler(console)

    importlib.import_module('commands')  # initialize the commands

    client = discord.Client()
    commandreg = util.ListenerRegistry(client, [resources.CONFUCIUS], **args)

    commandreg.add_listener(*util.listenerfinder.initialize_discovered())

    main_logger.debug('Bot has %s listeners: %s',
                      len(commandreg.commands),
                      ', '.join(map(lambda l: type(l).__name__, commandreg.commands)))

    @client.event
    async def on_ready():
        main_logger.info('Logged in as ' + client.user.name)
        main_logger.info('Add me to your server using {url}'.format(
            url=resources.URL.format(bot_id=client.user.id, scope='bot', permissions='11264'))
        )
        await commandreg.on_start()

    @client.event
    async def on_message(msg):
        await commandreg.on_message(msg)

    @client.event
    async def on_member_join(member):
        await commandreg.on_member_join(member)

    main_logger.setLevel(logging.WARN)
    main_logger.info('Received token ' + token)

    main_logger.info('Running preload tasks...')
    asyncio.get_event_loop().run_until_complete(commandreg.on_pre_load())  # Preload tasks
    run_bot()


def run_bot():

    is_running = True
    while is_running:

        try:
            main_logger.info('Starting bot...')
            client.loop.run_until_complete(client.start(token))  # Start the bot

        except KeyboardInterrupt:  # It has been stopped?

            client.loop.run_until_complete(client.logout())
            pending = asyncio.Task.all_tasks()
            gathered = asyncio.gather(*pending)
            try:
                gathered.cancel()
                client.loop.run_until_complete(gathered)
                gathered.exception()
            finally:
                is_running = False

        except discord.ConnectionClosed as e:  # We lost connection?

            main_logger.exception(e)
            main_logger.info('Retrying connection in 5 seconds...')
            time.sleep(5)

        finally:
            client.loop.close()


def get_args():

    keyargs, args = getopt.getopt(sys.argv[1:], 't:l:')
    out = {}

    if len(args) > 0:
        with open(args[0], 'r') as f:
            out = json.loads(f.read())
    elif len(keyargs) > 0:
        for k, arg in keyargs:
            if k == '-t':
                out['token'] = arg
            elif k == '-l':
                out['loglevel'] = int(arg)
    else:
        out = os.environ

    print(out)
    return out

if __name__ == '__main__':
    main()
