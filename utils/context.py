import discord
from discord.ext import commands

import io
import traceback
import contextlib
from asyncio import TimeoutError


class Context(commands.Context):

    @property
    def session(self):
        return self.bot.session

    async def confirm_prompt(self, msg):
        """Asks author for confirmation, returns True if confirmed, False if user typed abort or timed out"""
        def confirm(m):
            if self.author.id != m.author.id or self.channel.id != m.channel.id:
                return False
            return m.content.lower() in ('**confirm**', 'confirm', '**abort**', 'abort')

        prompt = await self.send(f'{msg}\n'
                                f'Please type **confirm** within 1 minute to continue or type **abort** if you change your mind.')

        try:
            reply = await self.bot.wait_for('message', check=confirm, timeout=60)
        except TimeoutError:
            await self.send('1 minute has passed. Aborting...', delete_after=5)
            return False
        else:
            choice = reply.content
            await reply.delete()
            if choice.lower() in ('**confirm**', 'confirm'):
                return True
            else:
                await self.send('Aborting...', delete_after=5)
                return False
        finally:
            with contextlib.suppress(discord.HTTPException):
                await prompt.delete()

    async def confirm_reaction(self, msg):
        emojis = ['<:tick:785940102353780736>', '<:cross:785940102542655539>']

        def confirm(r, u):
            return self.author.id == u.id and prompt == r.message and str(r.emoji) in emojis

        prompt = await self.send(f'{msg}\n'
                                f'Please react with <:tick:785940102353780736> within 1 minute to continue or <:cross:785940102542655539> if you change your mind.')
        for e in emojis:
            await prompt.add_reaction(e)
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=confirm, timeout=60)
        except TimeoutError:
            await self.send('1 minute has passed. Aborting...', delete_after=5)
            return False
        else:
            if str(reaction.emoji) == '<:tick:785940102353780736>':
                return True
            else:
                await self.send('Aborting...', delete_after=5)
                return False
        finally:
            with contextlib.suppress(discord.HTTPException):
                await prompt.delete()

    async def tick(self, value=True, reaction=True):
        emojis = {True:  '<:tick:785940102353780736>',
                  False: '<:cross:785940102542655539>',
                  None:  '<:greyTick:602811779810328596>'}
        emoji = emojis.get(value, '<:cross:785940102542655539>')
        if reaction:
            with contextlib.suppress(discord.HTTPException):
                await self.message.add_reaction(emoji)
        else:
            return emoji

    async def silent_delete(self, message=None):
        message = message or self.message
        with contextlib.suppress(discord.HTTPException):
            await message.delete()

    async def _upload_content(self, content, url='https://mystb.in'):
        async with self.bot.session.post(f'{url}/documents', data=content.encode('utf-8')) as post:
            return f'{url}/{(await post.json())["key"]}'

    async def upload_hastebin(self, content, url='https://mystb.in'):
        """Uploads content to hastebin and return the url"""
        try:
            return await self._upload_content(content, url)
        except:
            try:
                return await self._upload_content(content, 'https://hastebin.com')
            except:
                traceback.print_exc()

    async def safe_send(self, content, file=False, filename='message_too_long.txt', url='https://mystb.in', code=None , **kwargs):
        """Sends to ctx.channel if possible, upload to hastebin or send text file if too long"""
        cb = f'```{code}\n{content}\n```' if code is not None else content

        if len(cb) <= 2000:
            return await self.send(cb, **kwargs)
        elif file:
            fp = io.BytesIO(content.encode())
            return await self.send(file=discord.File(fp, filename=filename), **kwargs)
        else:
            hastebin_url = await self.upload_hastebin(self, content, url)
            return await self.send(f'Output too long, uploaded here instead: {hastebin_url}', **kwargs)

