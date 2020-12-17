import discord
from discord.ext import commands
import traceback
import io
import textwrap
from contextlib import redirect_stdout

import tabulate
from utils.common import cleanup_code, upload_hastebin


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    async def cog_check(self, ctx):
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner('Only my owner can use this command.')
        return True

    @commands.command(name='sql')
    async def run_query(self, ctx, *, query):
        query = cleanup_code(query)

        is_multiple = query.count(';') > 1
        if is_multiple:
            # fetch does not support multiple statements
            method = self.bot.pool.execute
        else:
            method = self.bot.pool.fetch

        try:
            results = await method(query)
        except Exception:
            return await ctx.send(f'```py\n{traceback.format_exc()}\n```')

        rows = len(results)
        if is_multiple or rows == 0:
            return await ctx.send(f'```\n{results}```')
        headers = list(results[0].keys())
        values = [list(map(repr, v)) for v in results]
        table = tabulate.tabulate(values, tablefmt='psql', headers=headers)
        if len(table) > 1000:
            url = await ctx.upload_hastebin(table)
            return await ctx.send(f'Output too long, uploaded to hastebin instead: <{url}>')

        await ctx.send(f'```\n{table}```')

    @commands.command(name='eval')
    async def _eval(self, ctx, *, code: str):
        """Evaluates python code in a single line or code block"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())
        code = cleanup_code(code)
        stdout = io.StringIO()
        to_compile = f'async def func():\n{textwrap.indent(code, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.safe_send(content=value, code='py')
            else:
                self._last_result = ret
                await ctx.safe_send(content=f'{value}{ret}', code='py')

    @commands.command(name="shutdown")
    async def logout(self, ctx):
        """
        Logs out the bot.
        """
        if not await ctx.confirm_reaction('Shutdown?'):
            return
        await ctx.message.add_reaction('\U0001f620')
        await ctx.bot.logout()

    @commands.command(name='load')
    async def load_cog(self, ctx, *, cog: str):
        """Loads a Module.
        Accepts dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'<:redTick:602811779474522113> {type(e).__name__} - {e}')
        else:
            await ctx.send(f'<:greenTick:602811779835494410> loaded {cog}')

    @commands.command(name='unload')
    async def unload_cog(self, ctx, *, cog: str):
        """ Unloads a Module.
        Accepts dot path. e.g: cogs.owner"""
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'<:redTick:602811779474522113> {type(e).__name__} - {e}')
        else:
            await ctx.send(f'<:greenTick:602811779835494410> unloaded {cog}')

    @commands.command(name='reload')
    async def reload_cog(self, ctx, *, cog: str):
        """Reloads a Module.
        Accepts dot path e.g: cogs.owner"""
        try:
            try:
                self.bot.reload_extension(cog)
            except commands.ExtensionNotLoaded:
                self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'<:redTick:602811779474522113> {type(e).__name__} - {e}')
        else:
            await ctx.send(f'<:greenTick:602811779835494410> reloaded {cog}')


def setup(bot):
    bot.add_cog(Owner(bot))
