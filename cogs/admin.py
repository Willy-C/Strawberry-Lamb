import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.id == self.bot.get_guild(758919988965801984).owner_id or await ctx.bot.is_owner(ctx.author)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            ctx.local_handled = True
            # Silently ignore commands not used by the owner

    def get_bot_member(self, ctx):
        if ctx.guild is None:
            botmember = self.bot.guilds[0].me
        else:
            botmember = ctx.me
        return botmember

    @commands.group(name='presence', invoke_without_command=True, case_insensitive=True)
    async def change_presence(self, ctx):
        await ctx.send_help(ctx.command)

    @change_presence.command(name='listen', aliases=['l'])
    async def listen(self, ctx, *, name):
        botmember = self.get_bot_member(ctx)
        status = botmember.status
        await self.bot.change_presence(activity=discord.Activity(name=name, type=discord.ActivityType.listening),
                                       status=status)
        await ctx.tick()

    @change_presence.command(name='playing', aliases=['play', 'p'])
    async def playing(self, ctx, *, name):
        botmember = self.get_bot_member(ctx)
        status = botmember.status
        await self.bot.change_presence(activity=discord.Game(name=name), status=status)
        await ctx.tick()

    @change_presence.command(name='streaming', aliases=['s'])
    async def streaming(self, ctx, name, url=None):
        botmember = self.get_bot_member(ctx)
        status = botmember.status
        url = url or 'https://www.twitch.tv/directory'
        await self.bot.change_presence(activity=discord.Streaming(name=name, url=url), status=status)
        await ctx.tick()

    @change_presence.command(name='watching', aliases=['w'])
    async def watching(self, ctx, *, name):
        botmember = self.get_bot_member(ctx)
        status = botmember.status
        await self.bot.change_presence(activity=discord.Activity(name=name, type=discord.ActivityType.watching),
                                       status=status)
        await ctx.tick()

    @change_presence.command(name='competing', aliases=['c'])
    async def competing(self, ctx, *, name):
        botmember = self.get_bot_member(ctx)
        status = botmember.status
        await self.bot.change_presence(activity=discord.Activity(name=name, type=discord.ActivityType.competing),
                                       status=status)
        await ctx.tick()

    @change_presence.command(name='status')
    async def status(self, ctx, status):
        statuses = {'online': discord.Status.online,
                    'offline': discord.Status.invisible,
                    'invis': discord.Status.invisible,
                    'invisible': discord.Status.invisible,
                    'idle': discord.Status.idle,
                    'dnd': discord.Status.dnd}
        status = status.lower()
        if status not in statuses:
            return await ctx.send(f'Not a valid status! Choose: [{", ".join(statuses.keys())}]')
        botmember = self.get_bot_member(ctx)
        activity = botmember.activity
        await self.bot.change_presence(status=statuses[status], activity=activity)
        await ctx.tick()

    @change_presence.command()
    async def clear(self, ctx):
        await self.bot.change_presence()
        await ctx.tick()

    @change_presence.command()
    async def reset(self, ctx):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='you :)'))
        await ctx.tick()


def setup(bot):
    bot.add_cog(Admin(bot))
