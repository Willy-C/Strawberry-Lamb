import discord
from discord.ext import commands
from utils.time import human_timedelta


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx, simple: bool = False):
        """Returns the bot's uptime
        Pass in True to view simplified time"""
        await ctx.send(f'Uptime: {human_timedelta(self.bot.start_time, accuracy=None, brief=simple, suffix=False)}')


def setup(bot):
    bot.add_cog(Meta(bot))
