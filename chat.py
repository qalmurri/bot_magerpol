import discord
import json
import asyncio
from discord.ext import commands

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

async def update_message():
    await bot.wait_until_ready()
    channel_chats = bot.get_channel(1121995813770493992) 
    # Ganti CHANNEL_ID dengan ID text channel yang diinginkan
    message = await channel_chats.send('yang akan diperbarui')
    
    while not bot.is_closed():
        try:
            # Melakukan perbaruan pesan di text channel
            data = load_data()
            chats = data['chats']
            sorted_chats = sorted(chats.items(), key=lambda x: x[1], reverse=True)
            output = "Chats:\n"
            for i, (user_id, message_count) in enumerate(sorted_chats, start=1):
                try:
                    user = await bot.fetch_user(int(user_id))
                    output += f"{i}. `{user.name}` {message_count} pesan\n"
                except discord.NotFound:
                    output += f"{i}. User tidak ditemukan: {message_count} pesan\n"

            await message.edit(content=output)

            # Menunggu interval waktu sebelum melakukan perbaruan selanjutnya
            await asyncio.sleep(2)  # Ganti 5 dengan interval waktu dalam detik
        except discord.errors.NotFound:
            # Pesan tidak ditemukan, kemungkinan sudah dihapus, maka kirim pesan baru
            message = await channel_chats.send('yang akan diperbarui')

# Simpan leaderboard dan level ke file JSON
def save_data(data):
    with open('chat.json', 'w') as file:
        json.dump(data, file)

# Perbarui jumlah pesan pengguna dalam leaderboard
def update_chats(data, user_id):
    chats = data['chats']
    if str(user_id) in chats:
        chats[str(user_id)] += 1
    else:
        chats[str(user_id)] = 1

# Perbarui level pengguna
def update_chat_levels(data, user_id, message_count):
    chat_levels = data['chat_levels']
    if str(user_id) in chat_levels:
        current_level = chat_levels[str(user_id)]
        if message_count >= current_level * 10:
            chat_levels[str(user_id)] += 1
    else:
        chat_levels[str(user_id)] = 1

# Event listener untuk mengupdate leaderboard dan level setiap kali ada pesan baru
@bot.event
async def on_message(message):
    if not message.author.bot:
        data = load_data()
        user_id = message.author.id

        update_chats(data, user_id)
        update_chat_levels(data, user_id, data['chats'][str(user_id)])

        save_data(data)
    await bot.process_commands(message)




# Menjalankan bot
bot.run('OTY3MTcwODYxNTA3NDQwNjUw.GPLjOD.h93uoLLI57oJBy1whpAZXc7TSBGRiY5QVxNjAo')
