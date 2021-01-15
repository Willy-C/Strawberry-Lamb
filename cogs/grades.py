import discord
from discord.ext import commands
from tabulate import tabulate

from datetime import datetime

from utils.converters import CaseInsensitiveMember

PROF_ROLE = 763274450107367425

GRADES = {'A+': 12,
          'A' : 11,
          'A-': 10,
          'B+': 9,
          'B' : 8,
          'B-': 7,
          'C+': 6,
          'C' : 5,
          'C-': 4,
          'D+': 3,
          'D' : 2,
          'D-': 1,
          'F' : 0}

ACADEMIES = ['business',
             'coaching',
             'coding',
             'entrepreneurship',
             'finance',
             'marketing',
             'partnership',
             'scaling',
             'stocks',
             'tech']


class Grade(commands.Converter):
    async def convert(self, ctx, argument):
        argument = argument.upper()
        role = GRADES.get(argument)
        if role is None:
            raise commands.BadArgument(f'{argument} is not a valid grade.\n'
                                       f'Must be one of: `{", ".join(GRADES.keys())}`')
        return argument, discord.Object(role)


class Academy(commands.Converter):
    async def convert(self, ctx, argument):
        argument = argument.lower()
        if argument in ACADEMIES:
            return argument
        aliases = {'coach': 'coaching',
                   'code': 'coding',
                   'entrepreneur': 'entrepreneurship',
                   'finances': 'finance',
                   'stock': 'stocks',
                   'market': 'marketing'}
        if argument in aliases:
            return aliases.get(argument)
        raise commands.BadArgument(f'"{argument}" is not a valid academy!\n'
                                   f'Must be one of: `{", ".join(ACADEMIES)}`')


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


def sort_args(arg1, arg2):
    """Returns (grade, academy)"""
    if arg1 in GRADES:
        if arg2 in GRADES:
            raise commands.BadArgument('Unable to find that academy')
        elif arg2 in ACADEMIES:
            return arg1, arg2
    elif arg1 in ACADEMIES:
        if arg2 in ACADEMIES:
            raise commands.BadArgument('Invalid Grade')
        elif arg2 in GRADES:
            return arg2, arg1


class Grading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, case_insensitive=True)
    @is_prof()
    async def grade(self, ctx, grade: Grade, academy: Academy, *, user: CaseInsensitiveMember):
        """Grade a student"""
        grade, role = grade
        # await single_role_in(user, grade[1], list(GRADES.values()))
        await ctx.send(f'{user.mention} is given the grade of `{grade}` for `{academy.capitalize()}`')
        query = '''INSERT INTO grades(student, teacher, class, grade, "when")
                   VALUES($1, $2, $3, $4, $5);'''
        await self.bot.pool.execute(query, user.id, ctx.author.id, academy, grade, datetime.utcnow())
        await ctx.tick()

    @grade.command()
    @is_prof()
    async def remove(self, ctx, academy: Academy, *, user: CaseInsensitiveMember):
        """Remove the last grade for a student from an academy"""
        query = '''SELECT * FROM grades 
                   WHERE student = $1 AND class = $2
                   ORDER BY entry DESC LIMIT 1;'''
        record = await self.bot.pool.fetchrow(query, user.id, academy)
        if record is None:
            return await ctx.send(f'I am unable to find any grades given to {user.mention} for {academy}',
                                  allowed_mentions=discord.AllowedMentions.none())
        if not await ctx.confirm_reaction(f'Are you sure you want to remove the grade of {record["grade"]} given by {ctx.guild.get_member(record["teacher"]).mention} for {record["class"]} for {user.mention}?',
                                          discord.AllowedMentions(users=[discord.Object(record["teacher"])])): return
        # new_roles = [r for r in user.roles if r.id not in list(GRADES.values())]
        # await user.edit(roles=new_roles)
        await ctx.send(f'Removed the last grade ({record["grade"]}) for {user.mention} for {academy}')
        query = '''DELETE FROM grades WHERE entry = $1;'''
        await self.bot.pool.execute(query, record['entry'])
        await ctx.tick()

    async def get_latest_grades(self, user: discord.Member):
        query = '''SELECT * FROM grades WHERE student=$1;'''
        records = await self.bot.pool.fetch(query, user.id)
        latest_grades = {a: None for a in ACADEMIES}
        for record in records:
            if latest_grades[record['class']] is not None:
                if GRADES[record['grade']] > GRADES[latest_grades[record['class']]]:
                    latest_grades[record['class']] = (record['grade'], record['teacher'])
            else:
                latest_grades[record['class']] = (record['grade'], record['teacher'])
        return {k.capitalize(): v for k, v in latest_grades.items()}

    @commands.group(invoke_without_command=True, case_insensitive=True, aliases=['rc'])
    async def reportcard(self, ctx, *, user: CaseInsensitiveMember=None):
        """Displays a student's report card.
        If no user is given, defaults to command invoker.
        If neither desktop/mobile was specified then it will try to detect whether the invoker is on mobile or not"""
        if ctx.author.is_on_mobile():
            await self.mobile(ctx, user=user)
        else:
            await self.desktop(ctx, user=user)

    @reportcard.command()
    async def desktop(self, ctx, *, user: CaseInsensitiveMember=None):
        """Displays a student's report card in a table
        If no user is given, defaults to command invoker."""
        user = user or ctx.author
        grades = await self.get_latest_grades(user)
        table = [[a, g[0], ctx.guild.get_member(g[1])] if g is not None else [a, None, None] for a, g in grades.items()]
        tabulated = tabulate(table, headers=['Academy', 'Grade', 'Professor'], tablefmt='fancy_grid')
        e = discord.Embed(description=f'```\n{tabulated}\n```',
                          color=user.colour,
                          timestamp=datetime.utcnow())
        e.set_author(name=user, icon_url=user.avatar_url)
        await ctx.send(embed=e)

    @reportcard.command()
    async def mobile(self, ctx, *, user: CaseInsensitiveMember=None):
        """Displays a student's report card in a mobile-friendly way
        If no user is given, defaults to command invoker."""
        user = user or ctx.author
        grades = await self.get_latest_grades(user)
        description = '\n'.join([f'{a} :: **{g[0]}** ({ctx.guild.get_member(g[1])})' if g is not None else f'{a} :: No grade' for a, g in grades.items()])
        e = discord.Embed(title='Report Card',
                          description=description,
                          color=user.colour,
                          timestamp=datetime.utcnow())
        e.set_author(name=user, icon_url=user.avatar_url)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Grading(bot))
