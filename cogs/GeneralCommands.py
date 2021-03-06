import re

import discord
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv

from Util import Math
from context.MongoPosts import UserPost
from context.UserContext import UserContext


class GeneralCommands(commands.Cog):

    def __init__(self, bot_obj):
        load_dotenv()
        self.bot = bot_obj

    # events listener
    @commands.Cog.listener()
    async def on_ready(self):

        print('Bot is online')
        await self.bot.change_presence(activity=discord.Game('!help'))

    @commands.Cog.listener()
    async def on_message(self, message):

        pattern = re.compile('[0-9]d|D[0-9]')

        if pattern.search(message.content):
            result = await Math.dice_calculator(message.content)
            await message.channel.send(f'{message.author.mention}  →  {result}  ( {str(message.content)} )')

    # commands listener
    @commands.command(name='ping')
    async def ping(self, ctx):
        embed = discord.Embed(description=f'my current ping is: {round(self.bot.latency * 1000)}ms')
        await ctx.send(embed=embed)

    @commands.command(name='clear')
    async def clear(self, ctx):

        if ctx.author.guild_permissions.administrator:

            current_channel = ctx.message.channel

            # checking the current amount of messages to delete
            messages = await current_channel.history(limit=None).flatten()

            # deleting messages from the channel
            await current_channel.purge(limit=len(messages))

            embed = discord.Embed(description=f'Deleted {len(messages)} messages from this channel.')
            await ctx.send(embed=embed)
            messages.clear()

        else:
            embed = discord.Embed(description=f"you don't have enough permission to use this command")
            await ctx.send(embed=embed)

    @commands.command(name='register')
    async def register(self, ctx):
        current_author = str(ctx.author)
        guild_id = str(ctx.guild)
        author_id = current_author[current_author.find('#'):]

        print(current_author)
        print(author_id)

        user_context = UserContext(author_id, guild_id)

        if user_context.user_doc is None or not author_id == user_context.user_name:
            post = UserPost(user_name=author_id, guild_id=guild_id)
            post.save()
            embed = discord.Embed(description=f'Registered successfully')
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f'User already registered')
            await ctx.send(embed=embed)

    @commands.command(name='unregister')
    async def unregister(self, ctx, member: discord.Member):

        if ctx.author.guild_permissions.administrator:

            current_author = str(member)
            guild_id = str(ctx.guild)
            author_id = current_author[current_author.find('#'):]

            print(current_author)
            print(author_id)

            user_context = UserContext(author_id, guild_id)

            if user_context is not None and author_id == user_context.user_name:
                user_context.delete()
                embed = discord.Embed(description=f'Deleted successfully')
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f"User was not registered")
                await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description=f"you don't have enough permission to use this command")
            await ctx.send(embed=embed)

    @commands.command(name='profile')
    async def profile(self, ctx, *member: discord.Member):
        if len(member) > 0:
            user_obj = member[0]
        else:
            user_obj = await commands.MemberConverter().convert(ctx, str(ctx.author))  # get the author obj

        guild_id = str(ctx.guild)
        user_id = str(user_obj)[str(user_obj).find('#'):]
        user_name = str(user_obj)[:str(user_obj).find('#')]
        user_context = UserContext(user_id, guild_id)
        user_avatar = user_obj.avatar_url

        embed = discord.Embed(title='Profile', colour=discord.Colour.blue())

        if user_context.user_doc is not None:
            embed.set_author(name=user_name, icon_url=user_avatar)
            embed.set_thumbnail(url=user_avatar)
            embed.add_field(name='Money', value=f'$ {str(user_context.user_money)}', inline=False)
            embed.add_field(name='Games Won', value=user_context.user_games_won, inline=False)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f'User {user_obj} not registered yet')
            await ctx.send(embed=embed)

    # command for testing purposes
    @commands.command(name='give_money')
    async def give_money(self, ctx, member: discord.Member, value):

        if ctx.author.guild_permissions.administrator:

            if member is not None:
                guild_id = str(ctx.guild)
                member_id = str(member)[str(member).find('#'):]
                result = UserContext(member_id, guild_id).receive_money(float(value))

                if result:
                    embed = discord.Embed(description=f'User {member} received ${float(value)} sucessfully!')
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=f'User did not received the money correctly')
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(description=f"user specified doesn't exists")
                await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description=f"you don't have enough permission to use this command")
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(GeneralCommands(client))
