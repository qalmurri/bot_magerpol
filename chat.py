import discord
import json
import asyncio
import time
import random
from discord.ext import commands

notif_levelup = 1122171407363747860
leaderboard_chat = 1121995813770493992

intents = discord.Intents.all()
intents.typing = False
intents.presences = False
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Connected as {bot.user.name}')
    await update_message()

 # Inisialisasi leaderboard dan level dari file JSON
def load_data():
    try:
        with open('chat.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {'chats': {}, 'chat_levels': {}}
    return data

# bot mulai, auto update message leaderboard
async def update_message():
    await bot.wait_until_ready()
    channel_chats = bot.get_channel(leaderboard_chat)
    message = await channel_chats.send(':arrows_counterclockwise:')
    while not bot.is_closed():
        try:
            #time.strftime('%Y-%m-%d %H:%M:%S')
            date = time.strftime('%H:%M:%S')
            # Melakukan perbaruan pesan di text channel
            data = load_data()
            chats = data['chats']
            levels = data['chat_levels']
            combined_data = [(user_id, chats[user_id], levels[user_id]) for user_id in chats]
            print(combined_data)
#            for user_id, value in combined_data.items():
#                chat_value = value["chat"]
#                level_value = value["level"]
#                print(f"User ID: {user_id}, Chat: {chat_value}, Level: {level_value}")
            sorted_chats = sorted(combined_data, key=lambda x: x[1], reverse=True)
            output = f"{date}\nUpdate Chats:\n" 
            for i, (user_id, message_count, level) in enumerate(sorted_chats, start=1):
                try:
                    user = await bot.fetch_user(int(user_id))
                    output += f"{i}. `{user.name}({level})` {message_count} pesan\n"
                except discord.NotFound:
                    output += f"{i}. User tidak ditemukan: {message_count} pesan\n"
            await message.edit(content=output)
            # Menunggu interval waktu sebelum melakukan perbaruan selanjutnya
            await asyncio.sleep(60)  # Ganti 5 dengan interval waktu dalam detik
        except discord.errors.NotFound:
            # Pesan tidak ditemukan, kemungkinan sudah dihapus, maka kirim pesan baru
            message = await channel_chats.send(':arrows_counterclockwise:')

# save semua item ke file json
def save_data(data):
    with open('chat.json', 'w') as file:
        json.dump(data, file)

# memperbarui jumlah pesan user di leaderboard
def update_chats(data, user_id):
    chats = data['chats']
    if str(user_id) in chats:
        chats[str(user_id)] += 1
    else:
        chats[str(user_id)] = 1

# Memperbarui level user
async def update_chat_levels(data, user_id, message_count):
    chat_levels = data['chat_levels']
    if str(user_id) in chat_levels:
        current_level = chat_levels[str(user_id)]
        if message_count >= current_level * 5:
            chat_levels[str(user_id)] += 1

            #kirim pesan ke channel jika level up
            levelup = chat_levels[str(user_id)]
            channel_chats = bot.get_channel(notif_levelup)

            texts = [f"Selamat <@{str(user_id)}>, kategori chat mu naik ke level {levelup}.", f"Anjay! Chat <@{str(user_id)}> sekarang di level {levelup}.", f"<@{str(user_id)}> yang jarang tidur, Chat bisa level {levelup}."]
            random_text = random.choice(texts)
            await channel_chats.send(random_text)
    else:
        chat_levels[str(user_id)] = 1

# Event listener untuk mengupdate leaderboard dan level setiap kali ada pesan baru
@bot.event
async def on_message(message):
    if not message.author.bot:
        data = load_data()
        user_id = message.author.id
        update_chats(data, user_id)
        await update_chat_levels(data, user_id, data['chats'][str(user_id)])
        
        save_data(data)
    await bot.process_commands(message)

#command profile
@bot.command()
async def profile(ctx):
    data = load_data()
    chats = data['chats']
    levels = data['chat_levels']
    author_id = str(ctx.author.id)
    if author_id in chats and author_id in levels:
        chat_count = chats[author_id]
        level = levels[author_id]
        profile_message = f"<@{author_id}> Chat: {chat_count} ({level})"
        await ctx.send(profile_message)
    else:
        await ctx.send("Profile not found.")

# Menjalankan bot
bot.run('OTY3MTcwODYxNTA3NDQwNjUw.GPLjOD.h93uoLLI57oJBy1whpAZXc7TSBGRiY5QVxNjAo')
