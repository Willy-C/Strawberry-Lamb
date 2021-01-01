import discord
from discord.ext import commands


def can_manage_messages():
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.channel.permissions_for(ctx.author).manage_messages:
            return True
        raise commands.MissingPermissions(['Manage Messages'])
    return commands.check(predicate)


def is_admin():
    async def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.author.guild_permissions.administrator:
            return True
        raise commands.MissingPermissions(['Administrator'])
    return commands.check(predicate)
