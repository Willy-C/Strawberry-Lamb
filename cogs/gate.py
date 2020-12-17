import discord
from discord.ext import commands

GUILD = 758919988965801984
SUGGESTION_CHANNEL = 766154386694471681
BOXOFFICE_CHANNEL = 763482832277995541
SCHOOLGATE_CHANNEL = 758919988965801988
RULES_CHANNEL = 777651693059178499

UPVOTE = '<:tick:785940102353780736>'
DOWNVOTE = '<:cross:785940102542655539>'


class SchoolGate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild and message.guild.id != GUILD:
            return
        if message.channel.id == SUGGESTION_CHANNEL:
            await message.add_reaction(UPVOTE)
            await message.add_reaction(DOWNVOTE)
        elif message.channel.id == BOXOFFICE_CHANNEL:
            await message.add_reaction(UPVOTE)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != GUILD:
            return
        channel = self.bot.get_channel(SCHOOLGATE_CHANNEL)
        if channel is None:
            return
        description = f'Welcome, {member}, we’re so happy to have you! To complete your enrollment, make sure to read and verify you’ve read our rules here: <#{RULES_CHANNEL}>'
        e = discord.Embed(title=member.guild.name,
                          color=0xfadce2,
                          description=description)
        e.set_image(url='https://cdn.discordapp.com/attachments/759182646202335264/781762594716647454/image0.gif')
        await channel.send(member.mention, embed=e)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != GUILD:
            return
        channel = self.bot.get_channel(SCHOOLGATE_CHANNEL)
        if channel is None:
            return
        await channel.send(f'{member.mention} has transferred away from {member.guild}, we’ll miss you!')


def setup(bot):
    bot.add_cog(SchoolGate(bot))
