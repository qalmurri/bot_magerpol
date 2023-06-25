import discord
from discord.ext import commands
import json
import time

intents = discord.Intents.default()
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Fungsi untuk memuat data dari file JSON
def load_data():
    try:
        with open('voice.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {'join': {}}
    return data

# Fungsi untuk menyimpan data ke file JSON
def save_data(data):
    with open('voice.json', 'w') as file:
        json.dump(data, file)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_voice_state_update(member, before, after):
    # Memuat data dari file JSON
    data = load_data()

    # Mendapatkan ID pengguna
    user_id = str(member.id)

    # Mengecek apakah pengguna ada dalam data
    if user_id not in data['join']:
        data['join'][user_id] = {'status': 0, 'total_time': 0}

    # Mengecek status pengguna di voice channel
    if after.channel:
        data['join'][user_id]['status'] = 1
        data['join'][user_id]['start_time'] = time.time()
    else:
        data['join'][user_id]['status'] = 0
        if 'start_time' in data['join'][user_id]:
            total_time = time.time() - data['join'][user_id]['start_time']
            data['join'][user_id]['total_time'] += total_time
            del data['join'][user_id]['start_time']

    # Menyimpan data ke file JSON
    save_data(data)

bot.run('YOUR_DISCORD_BOT_TOKEN')
