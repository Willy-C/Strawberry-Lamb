import discord
from discord.ext import commands
from utils.common import single_role_in

PROF_ROLE = 763274450107367425

GRADES = {'A+': 793737141297086494,
          'A': 794150643722879016,
          'A-': 794152176792371210,
          'B+': 794150643786448918,
          'B': 794150645597732884,
          'B-': 794152178923077632,
          'C+': 794150645711110194,
          'C': 794150647296426024,
          'C-': 794152180961116190,
          'D+': 794151038000693248,
          'D': 794151040328925235,
          'D-': 794152184161763338,
          'F': 794151043070951434}


class Grade(commands.Converter):
    async def convert(self, ctx, argument):

        argument = argument.upper()
        role = GRADES.get(argument)
        if role is None:
            raise commands.BadArgument(f'Invalid grade, must be one of `{" ".join(GRADES.keys())}`')
        return argument, discord.Object(role)


def is_prof():
    async def predicate(ctx):
        if ctx.guild is None:
            raise commands.NoPrivateMessage
        if await ctx.bot.is_owner(ctx.author):
            return True
        if ctx.author.guild_permissions.administrator:
            return True
        role = discord.utils.get(ctx.author.roles, id=763274450107367425)
        if role is not None:
            return True
        raise commands.MissingRole('Professor')
    return commands.check(predicate)


class Profs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @is_prof()
    async def grade(self, ctx, grade: Grade, *, user: discord.Member):
        await single_role_in(user, grade[1], list(GRADES.values()))
        await ctx.send(f'{user.mention} is given the grade of {grade[0]}')
        await ctx.tick()

    @grade.command()
    @is_prof()
    async def clear(self, ctx, *, user: discord.Member):
        new_roles = [r for r in user.roles if r.id not in list(GRADES.values())]
        await user.edit(roles=new_roles)
        await ctx.send(f'Removed grade for {user.mention}')
        await ctx.tick()


def setup(bot):
    bot.add_cog(Profs(bot))
