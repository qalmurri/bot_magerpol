import discord
import json
import asyncio
import time
import random
from discord.ext import commands

mention_levelup = 1122171407363747860
leaderboard_chat = 1121995813770493992
leaderboard_voice = 1122395948111384658

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Connected as {bot.user.name}')
    await update_leaderboard()

# Inisialisasi leaderboard dan level dari file JSON
def load_data_chat():
    try:
        with open('chat.json', 'r') as file:
            data_chat = json.load(file)
    except FileNotFoundError:
        data_chat = {'chats': {}, 'chat_levels': {}}
    return data_chat

def load_data_voice():
    try:
        with open('voice.json', 'r') as file:
            data_voice = json.load(file)
    except FileNotFoundError:
        data_voice = {'join': {}, 'total':{}}
    return data_voice

# bot online, auto update leaderboard
async def update_leaderboard():
    await bot.wait_until_ready()
    channel_chats = bot.get_channel(leaderboard_chat)
    channel_voice = bot.get_channel(leaderboard_voice)
    message_chat = await channel_chats.send(':arrows_counterclockwise:')
    message_voice = await channel_voice.send(':arrows_counterclockwise:')
    while not bot.is_closed():
        try:
            #time.strftime('%Y-%m-%d %H:%M:%S')
            date = time.strftime('%H:%M:%S')
            # Melakukan perbaruan leaderboard_chat di text channel
            data_chat = load_data_chat()
            chats = data_chat['chats']
            levels = data_chat['chat_levels']
            combined_data = [(user_id, chats[user_id], levels[user_id]) for user_id in chats]
            # print(combined_data)
            sorted_chats = sorted(combined_data, key=lambda x: x[1], reverse=True)
            output = f"{date}\nUpdate Chats:\n" 
            for i, (user_id, message_count, level) in enumerate(sorted_chats, start=1):
                try:
                    user = await bot.fetch_user(int(user_id))
                    output += f"{i}. `{user.name}({level})` {message_count} pesan\n"
                except discord.NotFound:
                    output += f"{i}. User tidak ditemukan: {message_count} pesan\n"
            await message_chat.edit(content=output)

            # Melakukan perbaruan leaderboard_voice di text channel
            data_voice = load_data_voice()
            total_data = data_voice['total']
            #sorted_voice = sorted(total_data.items(), key=lambda x: x[1], reverse=True)
            leaderboard = sorted(total_data.items(), key=lambda x: x[1]['total_time'], reverse=True)

            output = f"{date}\nUpdate Voice:\n"
            for i, (user_id, stats) in enumerate(leaderboard, start=1):
                total_time = stats['total_time']
                struct_time = time.gmtime(total_time)
                formatted_time = time.strftime("%H:%M:%S", struct_time)
                #print(f"{i}. User ID: {user_id}, Total Time: {total_time}")
                try:
                    user = await bot.fetch_user(int(user_id))
                    output += f"{i}. `{user.name}` {formatted_time} detik\n"
                except discord.NotFound:
                    output += f"{i}. User tidak ditemukan: {formatted_time} detik\n"
            await message_voice.edit(content=output)

            # Menunggu interval waktu sebelum melakukan perbaruan selanjutnya/interval waktu dalam detik
            await asyncio.sleep(2)
        except discord.errors.NotFound:
            # Pesan tidak ditemukan, terhapus, maka kirim pesan baru
            message_chat = await channel_chats.send(':arrows_counterclockwise:')
            message_voice = await channel_voice.send(':arrows_counterclockwise:')

# save semua item ke file json
def save_data_chat(data_chat):
    with open('chat.json', 'w') as file:
        json.dump(data_chat, file)

def save_data_voice(data_voice):
    with open('voice.json', 'w') as file:
        json.dump(data_voice, file)

# memperbarui jumlah pesan user di leaderboard
def update_chats(data_chat, user_id):
    chats = data_chat['chats']
    if str(user_id) in chats:
        chats[str(user_id)] += 1
    else:
        chats[str(user_id)] = 1

# Memperbarui level user
async def update_chat_levels(data_chat, user_id, message_count):
    chat_levels = data_chat['chat_levels']
    if str(user_id) in chat_levels:
        current_level = chat_levels[str(user_id)]
        if message_count >= current_level * 5:
            chat_levels[str(user_id)] += 1

            #kirim pesan ke channel jika level up
            levelup = chat_levels[str(user_id)]
            channel_chats = bot.get_channel(mention_levelup)
            texts = [f"Selamat <@{str(user_id)}>, kategori chat mu naik ke level {levelup}.", f"Anjay! Chat <@{str(user_id)}> sekarang di level {levelup}.", f"<@{str(user_id)}> yang jarang tidur, Chat bisa level {levelup}."]
            random_text = random.choice(texts)
            await channel_chats.send(random_text)
    else:
        chat_levels[str(user_id)] = 1

# Event listener untuk mengupdate leaderboard dan level setiap kali ada pesan baru
@bot.event
async def on_message(message):
    if not message.author.bot:
        data_chat = load_data_chat()
        user_id = message.author.id
        update_chats(data_chat, user_id)
        await update_chat_levels(data_chat, user_id, data_chat['chats'][str(user_id)])
        
        save_data_chat(data_chat)
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    # Memuat data dari file JSON
    data_voice = load_data_voice()

    # Mendapatkan ID pengguna
    user_id = str(member.id)

    # Mengecek apakah pengguna ada dalam data
    if user_id not in data_voice['join']:
        data_voice['join'][user_id] = 0
        data_voice['total'][user_id] = {'start_time': 0, 'total_time': 0}

    # Mengecek status pengguna di voice channel
    if after.channel:
        data_voice['join'][user_id] = 1
        data_voice['total'][user_id]['start_time'] = time.time()
    else:
        data_voice['join'][user_id] = 0
        if 'start_time' in data_voice['total'][user_id]:
            total_time = time.time() - data_voice['total'][user_id]['start_time']
            data_voice['total'][user_id]['total_time'] += total_time
            del data_voice['total'][user_id]['start_time']

    # Menyimpan data ke file JSON
    save_data_voice(data_voice)

#command profile
@bot.command()
async def profile(ctx):
    data_chat = load_data_chat()
    chats = data['chats']
    levels = data_chat['chat_levels']
    author_id = str(ctx.author.id)
    if author_id in chats and author_id in levels:
        chat_count = chats[author_id]
        level = levels[author_id]
        profile_message = f"<@{author_id}> Chat: {chat_count} ({level})"
        await ctx.send(profile_message)
    else:
        await ctx.send("Profile not found.")

bot.run('OTY3MTcwODYxNTA3NDQwNjUw.GPLjOD.h93uoLLI57oJBy1whpAZXc7TSBGRiY5QVxNjAo')
