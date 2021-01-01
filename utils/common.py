import discord
import traceback
import typing


def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    if content.startswith('```'):
        split = content.split('\n')
        if ' ' not in split[0][3:].rstrip():  # Is language
            split = split[1:]
        else:
            split[0] = split[0][3:]  # Accidentally started coding on first line

        return '\n'.join(split).rstrip('` ')
    return content.strip('` \n')


async def upload_hastebin(bot, content, url='https://mystb.in'):
    """Uploads content to hastebin"""
    try:
        async with bot.session.post(f'{url}/documents', data=content.encode('utf-8')) as post:
            return f'{url}/{(await post.json())["key"]}'
    except:
        try:
            url = 'https://hastebin.com'
            async with bot.session.post(f'{url}/documents', data=content.encode('utf-8')) as post:
                return f'{url}/{(await post.json())["key"]}'
        except:
            traceback.print_exc()


async def single_role_in(member, role: typing.Union[int, discord.Role], all_roles: typing.List[int]):
    """Adds role to member and ensures member only has 1 role from all_roles"""
    new_roles = [r for r in member.roles if r.id not in all_roles]
    if isinstance(role, int):
        role = member.guild.get_role(role)
    new_roles.append(role)
    await member.edit(roles=new_roles)
