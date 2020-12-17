import discord
from discord.ext import commands
from collections import Counter


def can_manage_messages():
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.channel.permissions_for(ctx.author).manage_messages:
            return True
        raise commands.MissingPermissions(['Manage Messages'])
    return commands.check(predicate)


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

    async def _sad_clean(self, ctx, limit):
        counter = 0
        async for msg in ctx.history(limit=limit, before=ctx.message):
            if msg.author == ctx.me:
                await msg.delete()
                counter += 1
        return {str(self.bot.user): counter}

    async def _good_clean(self, ctx, limit):
        def check(m):
            return m.author == ctx.me or m.content.startswith(ctx.prefix)
        deleted = await ctx.channel.purge(limit=limit, check=check, before=ctx.message)
        return Counter(str(msg.author) for msg in deleted)

    @commands.command()
    @can_manage_messages()
    async def clean(self, ctx, limit: int = 25):
        """Cleans up the bot's messages"""
        if ctx.me.permissions_in(ctx.channel).manage_messages:
            spam = await self._good_clean(ctx, limit)
        else:
            spam = await self._sad_clean(ctx, limit)

        deleted = sum(spam.values())

        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed']
        if deleted:
            messages.append('')
            spammers = sorted(spam.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'- **{author}**: {count}' for author, count in spammers)

        await ctx.send('\n'.join(messages), delete_after=10)
        await ctx.tick()


def setup(bot):
    bot.add_cog(Mod(bot))
