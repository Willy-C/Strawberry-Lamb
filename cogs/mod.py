import discord
from discord.ext import commands


def is_mod():
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mod_level = {}

    def get_mod_level(self, member: discord.Member):
        role_ids = {role.id for role in member.roles}
        highest_role = max(set(self.mod_level) & role_ids, key=self.mod_level.get, default=None)
        return self.mod_level.get(highest_role, -float('inf'))

    def hierarchy_check(self, ctx, moderator: discord.Member, target: discord.Member):
        return (self.bot.owner_id == moderator.id or
                ctx.guild.owner_id == moderator.id or
                self.get_mod_level(moderator) > self.get_mod_level(target)) \
               and ctx.guild.owner_id != target.id

    def bot_hierarchy_check(self, ctx, target: discord.Member):
        return ctx.guild.me.top_role > target.top_role


def setup(bot):
    bot.add_cog(Mod(bot))
