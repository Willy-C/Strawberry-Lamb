import discord
from discord.ext import commands
import traceback

from utils.common import upload_hastebin


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.owner = None
        bot.on_error = self.on_error
        bot.loop.create_task(self.set_owner())

    async def set_owner(self):
        await self.bot.wait_until_ready()
        self.owner = (await self.bot.application_info()).owner

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""
        await self.bot.wait_until_ready()
        if getattr(ctx, 'local_handled', False):  # Check if handled by local error handlers
            return

        ignored = (commands.CommandNotFound, commands.CommandOnCooldown, commands.NotOwner)  # Tuple of errors to ignore
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'Command `{ctx.command}` has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.author.send(f'The command `{ctx.command}` cannot be used in Private Messages.')

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f'Bad argument: {error}')

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f'I cannot complete this command, you are missing the following permission{"" if len(error.missing_perms) == 1 else "s"}: {", ".join(error.missing_perms)}')

        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f'I cannot complete this command, I am missing the following permission{"" if len(error.missing_perms) == 1 else "s"}: {", ".join(error.missing_perms)}')

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send('Sorry, you cannot use this command')

        else:
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            await ctx.send(f'An unexpected error has occurred! My owner has been notified.\n'
                           f'If you really want to know what went wrong:\n'
                           f'||```py\n{tb[-1][:150]}```||')

            e = discord.Embed(title=f'An unhandled error occurred in {ctx.guild} | #{ctx.channel}',
                              description=f'Invocation message: {ctx.message.content}\n'
                                          f'[Jump to message]({ctx.message.jump_url})',
                              color=discord.Color.red())
            e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

            await self.owner.send(embed=e)
            fmt = "".join(tb)
            if len(fmt) >= 1980:
                url = await ctx.upload_hastebin(fmt)
                await self.owner.send(f'Traceback too long. {url}')
            else:
                await self.owner.send(f'```py\n{fmt}```')

    async def on_error(self, event, *args, **kwargs):
        await self.bot.wait_until_ready()
        await self.owner.send(f'An error occurred in event `{event}`')
        tb = "".join(traceback.format_exc())
        if len(tb) >= 1980:
            url = await upload_hastebin(self.bot, tb)
            await self.owner.send(f'Traceback too long. {url}')
        else:
            await self.owner.send(f'```py\n{tb}```')
