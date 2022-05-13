####################################################################################################
# Imports
####################################################################################################
import discord
from discord.ext import commands
import requests
import json
from keep_alive import keep_alive
import aiohttp
import os

####################################################################################################
# Creating an instance of this bot in the server, along with my token to run it
####################################################################################################
bot = commands.Bot(command_prefix='$')

####################################################################################################
# The token is imported from a .env file, you need to provide your own token here named 'DISCORD_TOKEN' or just the token if the app is locally run only
####################################################################################################
TOKEN = os.environ['DISCORD_TOKEN']

####################################################################################################
# Fetch a random quote
####################################################################################################
def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

####################################################################################################
# Logging the bot into the server and setting its activity status
####################################################################################################
@bot.event
async def on_ready():
  print(f'We have logged in as {bot.user}.')
  await bot.change_presence(activity = discord.Activity(
    type = discord.ActivityType.playing,
    name = '$commands'
  ))

####################################################################################################
# Whenever someone joins the server, the bot will DM them a welcome message
####################################################################################################
@bot.event
async def on_member_join(member):
  await member.create_dm()
  await member.dm_channel.send(
    f'{member.name}, welcome!'
  )

####################################################################################################
# The bot will send animated server emotes in place of anyone's message who cannot send them
####################################################################################################
@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if ":" == message.content[0] and ":" == message.content[-1]:
    emoji_name = message.content[1:-1]
    for emoji in message.guild.emojis:
      if emoji_name == emoji.name:
        await message.channel.send(str(emoji))
        await message.delete()
        break

  await bot.process_commands(message)

####################################################################################################
# Command to have the bot send a randomly fetched inspirational quote
####################################################################################################
@bot.command(name = "inspire", help = "Bot sends a random inspiration quote it fetched from an API")
async def send_inspirational_quote(ctx):
  quote = get_quote()
  await ctx.channel.send(quote)

####################################################################################################
# Command to have the bot ping whichever user is listed in the message and tell them to have a good day
####################################################################################################
@bot.command(name = 'hello', help = "Bot mentions someone else, telling them to have a good day.")
async def send_hello(ctx, *, user: discord.Member = None):
  if user:
    await ctx.channel.send(f"Hello, I hope {user.mention} has a good day!")
  else:
    await ctx.channel.send("Who do you want me to say hello to?")

####################################################################################################
# Command to have the bot call an API and send a random image of a dog with a fun fact on it
####################################################################################################
@bot.command(name = 'dog', help = "Bot fetches and posts a random image of a dog with a fun fact from online.")
async def call_API_for_dog(ctx):
  async with aiohttp.ClientSession() as session:
    request = await session.get('https://some-random-api.ml/img/dog') # Make a request
    dog_json = await request.json() # convert it to a JSON dictionary

    # this time we'll get the fact request
    request2 = await session.get('https://some-random-api.ml/facts/dog')
    facts_json = await request2.json()
  embed = discord.Embed(title = "Pup!", color = discord.Color.blue()) # create embed
  embed.set_image(url = dog_json['link']) # set the embed image to the value of the 'link' key
  embed.set_footer(text = facts_json['fact'])
  await ctx.send(embed = embed) # send the embed

####################################################################################################
# Command to have the bot call an API and send a random image of a cat
####################################################################################################
@bot.command(name = 'cat', help = "Bot fetches and posts a random image of a cat from online.")
async def call_API_for_cat(ctx):
  async with aiohttp.ClientSession() as session:
    request = await session.get('https://api.thecatapi.com/v1/images/search')
    cat_json = await request.json()
    embed = discord.Embed(title = "Kitty!", color = discord.Color.blue())
    embed.set_image(url = cat_json[0]['url'])
    await ctx.send(embed = embed)

####################################################################################################
# Command for having the bot create a channel, as long as the message author has a mod role of your choice
####################################################################################################
@bot.command(name = 'create', help = "Bot allows users with the role 'mod or something' to create a channel.")
@commands.has_role(os.environ['SERVER_MOD_ROLE'])
async def create_channel(ctx, *, args):
  guild = ctx.guild
  channel_name = args
  existing_channel = discord.utils.get(guild.channels, name = channel_name)
  if not existing_channel:
    print(f'Creating a new channel: {channel_name}')
    await guild.create_text_channel(channel_name)

####################################################################################################
# Command for having the bot create a category, as long as the message author has the role 'mod or something'
####################################################################################################
@bot.command(name = 'category', help = "Bot allows users with the role 'mod or something' to create a category.")
@commands.has_role(os.environ['SERVER_MOD_ROLE'])
async def create_category(ctx, *, args):
  guild = ctx.guild
  category_name = args
  existing_category = discord.utils.get(guild.categories, name = category_name)
  if not existing_category:
    print(f'Creating a new category: {category_name}')
    await guild.create_category(category_name)

####################################################################################################
# The bot checks if you have the correct role for using certain commands and denies you permission to use the command if you do not have the appropriate role
####################################################################################################
@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.errors.CheckFailure):
    await ctx.send("You do not have the correct role for this command.")

####################################################################################################
# Command to have the bot post the list of all available commands for easy access of what is allowed to do with the bot
####################################################################################################
@bot.command(name = 'commands', help = "Lists the commands and their uses for the bot.")
async def display_bot_commands(ctx):
  await ctx.channel.send("""> * $commands :- Lists all of the commands the bot can use.
  > * $create :- The bot allows users with a moderation role of your choice to create a new channel in the server
  > * $category :- The bot allows users with a moderation role of your choice to create a new category for channels in the server              
  > * $dog :- Sends a random picture of a dog with a dog fact.
  > * $cat :- Sends a random picture of a cat.
  > * $hello :- The bot tells someone of your choice to have a good day                       
  """)

####################################################################################################
# Calls the keep alive function, which keeps the server the bot is connected to online at all times
####################################################################################################
keep_alive()

####################################################################################################
# Tells the bot to run the token provided to it
####################################################################################################
bot.run(TOKEN)