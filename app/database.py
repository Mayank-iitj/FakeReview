import discord

# Create a client object
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Logged in as', client.user.name)

@client.event
async def on_message(message):
    # Check if the message is from a banned user
    if message.author.name == 'roryexe' and message.author.discriminator == '7':
        await message.channel.send(f'{message.author} has been banned!')
        await message.author.ban(reason='Banned for misbehavior')

client.run('MTQxNjYzMDM1MjEzODQ3MzQ4Mg.GaZakH.KbxM0OStnbBtrCFEVCEBZj5yVilFH_DrAj4BMo')