import discord
from discord.ext import commands
import os
import json
import asyncpg
import aiohttp
import asyncio
import traceback
import platform
from datetime import datetime
from sys import exit

from config import BOT_TOKEN, DBURI
from utils.context import Context


class StrawberryLamb(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('-'),
                         help_command=commands.MinimalHelpCommand(),
                         description='Bot for Strawberry Lamb server',
                         case_insensitive=True,
                         intents=discord.Intents.all(),
                         allowed_mentions=discord.AllowedMentions(everyone=False),
                         activity=discord.Activity(type=discord.ActivityType.watching, name='over the school'))

        self.start_time = datetime.utcnow()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.mod_level = {}

    async def on_ready(self):
        print(f'\nLogged in as: {bot.user.name} - {bot.user.id}\n'
              f'Python Version: {platform.python_version()}\n'
              f'Library Version: {discord.__version__}\n\n'
              f'Ready! {datetime.utcnow()}\n')

    async def get_context(self, message, *, cls=Context):
        return await super().get_context(message, cls=cls)

    async def close(self):
        await self.session.close()
        await super().close()
        await asyncio.wait_for(self.pool.close(), timeout=20)

    def get_mod_level(self, member: discord.Member):
        role_ids = {role.id for role in member.roles}
        highest_role = max(set(self.mod_level) & role_ids, key=self.mod_level.get, default=None)
        return self.mod_level.get(highest_role, -float('inf'))


async def db_init(con):
    await con.set_type_codec('jsonb', encoder=json.dumps, decoder=json.loads, schema='pg_catalog')
loop = asyncio.get_event_loop()
try:
    pool = loop.run_until_complete(asyncpg.create_pool(DBURI, init=db_init))
except Exception:
    print(f'\nUnable to connect to PostgreSQL, exiting...\n')
    traceback.print_exc()
    exit()
else:
    print('\nConnected to PostgreSQL\n')

bot = StrawberryLamb()
bot.pool = pool

ignored = []
extensions = ['jishaku']
extensions += [f'cogs.{f[:-3]}' for f in os.listdir('./cogs') if f.endswith('.py') and f[:-3] not in ignored]
total = len(extensions)
successes = 0
for ext in extensions:
    try:
        bot.load_extension(ext)
        print(f'Successfully loaded extension {ext}')
        successes += 1
    except Exception:
        print(f'Failed to load extension {ext}')
        traceback.print_exc()

print('-' * 52)
print(f'Successfully loaded {successes}/{total} extensions.')

bot.run(BOT_TOKEN)
