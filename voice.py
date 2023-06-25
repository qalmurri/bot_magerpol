import discord
from discord.ext import commands
import json

intents = discord.Intents.all()
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
        data['join'][user_id] = 0

    # Mengecek status pengguna di voice channel
    if after.channel:
        data['join'][user_id] = 1
    else:
        data['join'][user_id] = 0

    # Menyimpan data ke file JSON
    save_data(data)

bot.run('OTY3MTcwODYxNTA3NDQwNjUw.GPLjOD.h93uoLLI57oJBy1whpAZXc7TSBGRiY5QVxNjAo')
