import discord
from discord.ext import commands
import re
import asyncio


class DBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cd_regex = re.compile(r'Please wait another (\d{1,3}) minutes? until the server can be bumped')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id not in (764293682639536138, 781722149219991552) or message.author.id != 302050872383242240 or not message.embeds:
            return

        embed = message.embeds[0]
        if embed.color.value not in (0xeb4c61, 0x24b7b7):
            return
        if embed.color.value == 0xeb4c61:
            match = self.cd_regex.search(embed.description)
            if match is None:
                return
            minutes = int(match.group(1))
            time_to_sleep = minutes*60

        elif embed.color.value == 0x24b7b7:
            time_to_sleep = 120*60
        else:
            return

        await message.add_reaction('⏰')

        def check(r, u):
            return r.message == message and str(r.emoji) == '⏰' and not u.bot
        try:
            _, user = await self.bot.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            return
        finally:
            await message.clear_reaction('⏰')

        await asyncio.sleep(time_to_sleep)
        await message.channel.send(f'{user.mention} bump reminder')


def setup(bot):
    bot.add_cog(DBoard(bot))
