import discord                   
from discord import app_commands 
import json
import random
import asyncio

intents = discord.Intents.default()  
client = discord.Client(intents=intents) 
tree = app_commands.CommandTree(client) 

def check_role(user, role_name):
    return discord.utils.get(user.roles, name=role_name) is not None

def check_wallet(wallet):
    return wallet.startswith('0x')

def save_wallet(user, wallet):
    try:
        with open('wallets.json', 'r') as f:
            wallets = json.load(f)
    except FileNotFoundError:
        wallets = {}

    wallets[user] = wallet

    with open('wallets.json', 'w') as f:
        json.dump(wallets, f)

def check_role_x(user):
    return discord.utils.get(user.roles, name='Fairies Lead') is not None

def check_role_y(user):
    return discord.utils.get(user.roles, name='Fairies Holder') is not None

async def get_wallet_address(user):
    with open("wallets.json", "r") as f:
        data = json.load(f)
    return data.get(str(user), None) 

async def get_rarities_of_wallet(wallet_address):
    rarities = []

    with open('fairieswalet.json') as f:
        data = json.load(f)

    for nft in data:
        if nft['owner']['owner_address'] == wallet_address.lower():
            attributes = nft.get('attributes', [])
            for attribute in attributes:
                if attribute.get('trait_type') == 'Rarity':
                    rarities.append(attribute.get('value'))

    return rarities

def count_nfts_of_owner(json_data, owner_address):
    count = 0
    for item in json_data:
        if 'owner' in item and 'owner_address' in item['owner']:
            if item['owner']['owner_address'] == owner_address.lower():
                count += 1

    if count >= 20 :
        count == 20 
    return count

RARITY_MULTIPLIERS = {
    "Common": 1,
    "Epic": 5,
    "Unique": 20,
}

@tree.command(name = "showticket", description = "Show ticket") 
@app_commands.describe() 
async def showticket(interaction:discord.Interaction ):
    await interaction.response.defer(ephemeral=True)
    user = interaction.user
    sayac = 0
    wallet_address = await get_wallet_address(str(user))
    if wallet_address is not None:
        rarities = await get_rarities_of_wallet(wallet_address)
        for rarity in rarities:
            if rarity in RARITY_MULTIPLIERS:
                multiplier = RARITY_MULTIPLIERS[rarity]
                sayac += multiplier
    await interaction.followup.send(f"Your tickets : {sayac}",ephemeral=True)
        
@tree.command(name = "setwallet", description = "cüzdan adresinizi giriniz") 
@app_commands.describe(wallet = "cüzdan adresi") 
async def setwallet(interaction:discord.Interaction ,wallet:str ):
    user = interaction.user
    full_username = f'{user.name}#{user.discriminator}'
    if check_role(user, 'Fairies Holder') and check_wallet(wallet): 
        save_wallet(full_username, wallet)
        await interaction.response.defer(ephemeral=True)
        with open('fairieswalet.json') as f:
            data = json.load(f)
        many = count_nfts_of_owner(data, wallet)
        for _ in range(1,21):
            if 3 <= many <= 6:
                role = discord.utils.get(user.guild.roles, name=f'Level 1 Fairies Holder')
            elif 7 <= many <= 10:
                role = discord.utils.get(user.guild.roles, name=f'Level 2 Fairies Holder')
            elif 11 <= many <= 14:
                role = discord.utils.get(user.guild.roles, name=f'Level 3 Fairies Holder')
            elif 15 <= many <= 19:
                role = discord.utils.get(user.guild.roles, name=f'Level 4 Fairies Holder')
            elif many == 20:
                role = discord.utils.get(user.guild.roles, name=f'Level 5 Fairies Holder')
            else:
                role = None
        if role is not None:
            await user.add_roles(role)
            await interaction.followup.send("cüzdan adresi kaydedildi",ephemeral=True)
        
        else:
            await interaction.followup.send("cüzdan adresi kaydedildi",ephemeral=True)
    else:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Hatalı rol veya cüzdan adresi",ephemeral=True)

@tree.command(name = "startgiveaway", description = "Çekilişi başlatır") 
@app_commands.describe(duration = "Çekilişin süresi", winner_ = "Kazananların sayısı",title = "Çekiliş başlığı",description = "Açıklama",resim_url = "Resim url") 
async def startgiveaway(interaction:discord.Interaction, duration:int, winner_:int, title:str, description:str, resim_url:str):
    user = interaction.user
    if check_role_x(user):
        embed = discord.Embed(title = title, description = description, color = discord.Color.blue())
        embed.set_thumbnail(url = resim_url)
        message = await interaction.channel.send(embed = embed)
        await message.add_reaction("🎉")

        await asyncio.sleep(duration)

        message = await message.channel.fetch_message(message.id)
        users = []
        async for user in message.reactions[0].users():
            if user == client.user:
                continue
            wallet_address = await get_wallet_address(str(user))
            if wallet_address is not None:
                rarities = await get_rarities_of_wallet(wallet_address)
                for rarity in rarities:
                    if rarity in RARITY_MULTIPLIERS:
                        multiplier = RARITY_MULTIPLIERS[rarity]
                        users.extend([user] * multiplier)
        winners = random.sample(users, min(winner_, len(users)))
        for winner in winners:
            await interaction.channel.send("{} kazandı!".format(winner.mention))
    else:
        await interaction.followup.send("Bu komutu kullanma yetkiniz yok.",ephemeral=True)

@tree.command(name = "voteup", description = "oylama başlatır") 
@app_commands.describe(duration = "oylama süresi",title = "oylama başlığı",description = "Açıklama",resim_url = "Resim url") 
async def voteup(interaction:discord.Interaction, duration:int, title:str, description:str, resim_url:str):
    user = interaction.user
    if check_role_x(user):
        embed = discord.Embed(title = title, description = description, color = discord.Color.blue())
        embed.set_thumbnail(url = resim_url)
        message = await interaction.channel.send(embed = embed)
        await message.add_reaction("🇦")
        await message.add_reaction("🇧")

        await asyncio.sleep(duration)
        message = await message.channel.fetch_message(message.id)
        users_1 = []
        async for user in message.reactions[0].users():
            if user == client.user:
                continue
            wallet_address = await get_wallet_address(str(user))
            if wallet_address is not None:
                rarities = await get_rarities_of_wallet(wallet_address)
                for rarity in rarities:
                    if rarity in RARITY_MULTIPLIERS:
                        multiplier = RARITY_MULTIPLIERS[rarity]
                        users_1.extend([user] * multiplier)
        users_2 = []
        async for user in message.reactions[1].users():
            if user == client.user:
                continue
            wallet_address = await get_wallet_address(str(user))
            if wallet_address is not None:
                rarities = await get_rarities_of_wallet(wallet_address)
                for rarity in rarities:
                    if rarity in RARITY_MULTIPLIERS:
                        multiplier = RARITY_MULTIPLIERS[rarity]
                        users_2.extend([user] * multiplier)
        if len(users_2) > len(users_1) :
            await interaction.channel.send("🇧 kazandı !" .format())
        else : 
            await interaction.channel.send("🇦 kazandı !" .format())
    else:
        await interaction.followup.send("Bu komutu kullanma yetkiniz yok.",ephemeral=True)

@client.event
async def on_ready():
    print("Name: {}".format(client.user.name))
    await tree.sync()
    print("Ready!")

client.run("DISCORD_BOT_TOKEN")
