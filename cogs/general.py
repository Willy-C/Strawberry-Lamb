import discord
from discord.ext import commands

from utils import converters, checks


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_admin()
    @commands.bot_has_guild_permissions(manage_webhooks=True)
    async def quote(self, ctx, user: converters.CaseInsensitiveMember, *, message):
        """Send a message as someone else
        I require manage webhooks permission"""
        webhook = discord.utils.get(await ctx.channel.webhooks(),
                                    user=self.bot.user)

        if webhook is None:
            webhook = await ctx.channel.create_webhook(name='Quote')

        await webhook.send(message,
                           username=user.display_name,
                           avatar_url=user.avatar_url_as(format='png'),
                           allowed_mentions=discord.AllowedMentions.none())
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass


def setup(bot):
    bot.add_cog(General(bot))
