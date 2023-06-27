import discord
import json
import asyncio
import time
import random
from discord.ext import commands

# id channel
mention_levelup = 1122525320038322256
leaderboard_chat = 1122588810400759888
leaderboard_voice = 1122588822702653541

#permission
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Connected as {bot.user.name}')
    #auto update leaderboard
    await update_leaderboard()

# Inisialisasi chat dari file JSON
def load_data_chat():
    try:
        with open('chat.json', 'r') as file:
            data_chat = json.load(file)
    except FileNotFoundError:
        data_chat = {'chats': {}, 'chat_levels': {}}
    return data_chat

# Inisialisasi voice dari file JSON
def load_data_voice():
    try:
        with open('voice.json', 'r') as file:
            data_voice = json.load(file)
    except FileNotFoundError:
        data_voice = {'join': {}, 'total':{}, 'voice_levels': {}}
    return data_voice

# Inisialisasi chat dari file JSON
def load_data_xp():
    try:
        with open('experience.json', 'r') as file:
            data_xp = json.load(file)
    except FileNotFoundError:
        data_xp= {'xp': {}, 'xp_levels': {}}
    return data_xp

# auto update leaderboard
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
            chat_levels = data_chat['chat_levels']
            combined_data_chat = [(user_id, chats[user_id], chat_levels[user_id]) for user_id in chats]
            #print(combined_data)
            sorted_data_chat = sorted(combined_data_chat, key=lambda x: x[1], reverse=True)
            output = f"> :incoming_envelope: **LEADERBOARD CHAT** :incoming_envelope:\n> *Diupdate* {date}\n" 
            for i, (user_id, message_count, level) in enumerate(sorted_data_chat, start=1):
                try:
                    user = await bot.fetch_user(int(user_id))
                    output += f"{i}. `{user.name}` `({level})` `{message_count} pesan`\n"
                except discord.NotFound:
                    output += f"{i}. User tidak ditemukan: {message_count} pesan\n"
            #additional_text = f"> :incoming_envelope: **LEADERBOARD CHAT** :incoming_envelope:\n> *Diupdate* {date}\n" 
            #output += additional_text
            await message_chat.edit(content=output)

            # Melakukan perbaruan leaderboard_voice di text channel
            data_voice = load_data_voice()
            total = data_voice['total']
            level_data = data_voice['voice_levels']
            #combined_data_voice = [(user_id, total_data[user_id], level_data[user_id]) for user_id in total_data]
            combined_data_voice = [(user_id, total[user_id]['total_time'], level_data[user_id]) for user_id in total]
            sorted_chats_voice = sorted(combined_data_voice, key=lambda x: x[1], reverse=True)
            #sorted_voice = sorted(total_data.items(), key=lambda x: x[1], reverse=True)
            output = f"> :sound: **LEADERBOARD VOICE** :sound:\n> *Diupdate* {date}\n" 
            #for i, (user_id, stats, level_voice) in enumerate(sorted_chats_voice, start=1):
            #    total_time = stats['total_time']
            for i, (user_id, stats, level_voice) in enumerate(sorted_chats_voice, start=1):
                convert = stats
                # conver time
                convert2 = time.gmtime(convert)
                total_time = time.strftime("`%m/%d %H:%M:%S`", convert2)
                #print(f"{i}. User ID: {user_id}, Total Time: {total_time}")
                try:
                    user = await bot.fetch_user(int(user_id))
                    output += f"{i}. `{user.name}` `({level_voice})` {total_time}\n"
                except discord.NotFound:
                    output += f"{i}. User tidak ditemukan: {total_time} detik\n"
            #additional_text2 = f"> :sound: **LEADERBOARD VOICE** :sound:\n> *Diupdate* {date}\n" 
            #output += additional_text2
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

# save semua item ke file json
def save_data_voice(data_voice):
    with open('voice.json', 'w') as file:
        json.dump(data_voice, file)

# save semua item ke file json
def save_data_xp(data_xp):
    with open('experience.json', 'w') as file:
        json.dump(data_xp, file)

# memperbarui jumlah pesan user di leaderboard
def update_chats(data_chat, user_id):
    chats = data_chat['chats']
    if str(user_id) in chats:
        chats[str(user_id)] += 1
    else:
        chats[str(user_id)] = 1

def update_xp(data_xp, user_id):
    data_voice = load_data_voice()
    data_chat = load_data_chat()
    chats = data_chat['chats']
    xp = data_xp['xp']
    if str(user_id) in xp:
        if str(user_id) in chats and str(user_id) in data_voice['total']:
            convert = data_voice['total'][str(user_id)]['total_time']
            total_time = round(convert)
            score = (total_time + chats[str(user_id)]) * 3
        else:
            score = chats[str(user_id)] * 3
        xp[str(user_id)] = score  # Ubah menjadi xp[str(user_id)] += score agar nilai sebelumnya ditambahkan
    else:
        xp[str(user_id)] = 1

# Memperbarui level chat user
async def update_chat_levels(data_chat, user_id, message_count):
    chat_levels = data_chat['chat_levels']
    if str(user_id) in chat_levels:
        current_level = chat_levels[str(user_id)]
        if message_count >= current_level * 100:
            chat_levels[str(user_id)] += 1
            #kirim pesan ke channel jika level up
            chat_levelup = chat_levels[str(user_id)]
            channel_chats = bot.get_channel(mention_levelup)
            texts = [f"Selamat <@{str(user_id)}>, kategori chat mu naik ke level {chat_levelup}.", f"Anjay! Chat <@{str(user_id)}> sekarang di level {chat_levelup}.", f"<@{str(user_id)}> yang jarang tidur, Chat aja bisa level {chat_levelup}.", f"Keren <@{str(user_id)}> udah level {chat_levelup}, Chatingan sama siapa aja?", f"Lagi gabut ya <@{str(user_id)}>? sampe-sampe Chat udah level {chat_levelup}.", f"Maniak Chat ya <@{str(user_id)}>, gak kerasa Chat udah level {chat_levelup}.", f"<@{str(user_id)}> rajin amat nge-Chat, padahal sudah level {chat_levelup}.", f"Chat tanpa <@{str(user_id)}> sepi, Terima Kasih sudah level {chat_levelup}.", f"<@{str(user_id)}> Chat terbaik! Terima kasih sudah level {chat_levelup} :crown:", f"<@{str(user_id)}> :two_hearts: Chatmu sekarang sudah level {chat_levelup}."]
            random_text = random.choice(texts)
            await channel_chats.send(random_text)
    else:
        chat_levels[str(user_id)] = 1

# Memperbarui level XP user
async def update_xp_levels(data_xp, user_id):
    xp = data_xp['xp'][str(user_id)]
    xp_levels = data_xp['xp_levels']
    if str(user_id) in xp_levels:
        current_level = xp_levels[str(user_id)]
        if xp >= current_level * 1000:
            xp_levels[str(user_id)] += 1
            #kirim pesan ke channel jika level up
            xp_levelup = xp_levels[str(user_id)]
            print(xp_levelup)
            channel_xp = bot.get_channel(mention_levelup)
            texts = [f"Selamat <@{str(user_id)}>, kategori XP mu naik ke level {xp_levelup}."]
            random_text = random.choice(texts)
            await channel_xp.send(random_text)
    else:
        xp_levels[str(user_id)] = 1
    save_data_xp(data_xp)

# Memperbarui level voice user
async def update_voice_levels(data_voice, user_id):
    voice_levels = data_voice['voice_levels']
    if str(user_id) in voice_levels:
        current_level = voice_levels[str(user_id)]
        total_time = data_voice['total'][user_id]['total_time']
        level = total_time // 1600
        #1600 = 00:26:40
        if level >= current_level:
            voice_levels[str(user_id)] += 1
            voice_levelup = voice_levels[str(user_id)]
            channel_voice = bot.get_channel(mention_levelup)
            #{str(user_id)} {voice_levelup}
            randomvoice_levelup = [f"Gwendeng, wes bosen koen <@{str(user_id)}>? Voicemu wes level {voice_levelup}.", f"Selamat <@{str(user_id)}>, kategori voice mu naik ke level {voice_levelup}.", f"Sumpek a <@{str(user_id)}>? Voicemu wes level {voice_levelup}.", f"Emang kalo gak ada <@{str(user_id)}> voice jadi sepi, voicemu level {voice_levelup} .", f"<@{str(user_id)}> kenapa udahan? Padahal lagi seru-serunya, voicemu udah level {voice_levelup}.", f"<@{str(user_id)}> Voice terbaik! Terima kasih sudah level {voice_levelup}."]
            textvoice_levelup = random.choice(randomvoice_levelup)
            await channel_voice.send(textvoice_levelup)
    else:
        level[str(user_id)] = 1
    save_data_voice(data_voice)

# Event listener untuk mengupdate leaderboard dan level setiap kali ada pesan baru
@bot.event
async def on_message(message):
    if not message.author.bot:
        data_chat = load_data_chat()
        data_xp = load_data_xp()
        user_id = message.author.id
        update_chats(data_chat, user_id)
        update_xp(data_xp, user_id)
        await update_chat_levels(data_chat, user_id, data_chat['chats'][str(user_id)])
        await update_xp_levels(data_xp, user_id)
        save_data_chat(data_chat)
        save_data_xp(data_xp)
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    data_voice = load_data_voice()
    user_id = str(member.id)
    # Mengecek apakah pengguna ada dalam data
    if user_id not in data_voice['join']:
        data_voice['join'][user_id] = 0
        data_voice['total'][user_id] = {'total_time': 0, 'start_time': 0}
        data_voice['voice_levels'][user_id] = 0
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
            await update_voice_levels(data_voice, user_id)
    save_data_voice(data_voice)

#command profile
@bot.command()
async def profile(ctx):
    author_id = str(ctx.author.id)
    #statistik pesaan
    data_chat = load_data_chat()
    chats = data_chat['chats']
    chat_levels = data_chat['chat_levels']
    rank_chat = sorted(data_chat["chats"].items(), key=lambda x: x[1], reverse=True)
    user_rank_chat = next((i+1 for i, (uid, _) in enumerate(rank_chat) if uid == author_id), None)
    if author_id in chats and author_id in chat_levels:
        chats = chats[author_id]
        chat_levels = chat_levels[author_id]
    #statistik voicee
    data_voice = load_data_voice()
    voice_levels = data_voice['voice_levels']
    rank_voice = sorted(data_voice["total"].items(), key=lambda x: x[1]["total_time"], reverse=True)
    user_rank_voice = next((i+1 for i, (uid, _) in enumerate(rank_voice) if uid == author_id), None)
    if author_id in voice_levels and author_id in data_voice['total']:
        voice_levels = voice_levels[author_id]
        convert = data_voice['total'][author_id]['total_time']
        convert2 = time.gmtime(convert)
        total_time = time.strftime("`%m/%d %H:%M:%S`", convert2)
    #statistik xp
    data_xp = load_data_xp()
    xp = data_xp['xp']
    xp_levels = data_xp['xp_levels']
    rank_xp = sorted(data_xp["xp"].items(), key=lambda x: x[1], reverse=True)
    user_rank_xp = next((i+1 for i, (uid, _) in enumerate(rank_xp) if uid == author_id), None)
    if author_id in xp and author_id in xp_levels:
        xp = xp[author_id]
        xp_levels = xp_levels[author_id]
#pesan profile
        profile_message = f"<@{author_id}>\n`#{user_rank_chat}` `Chat` `({chat_levels})` `{chats} pesan`\n`#{user_rank_voice}` `Voice` `({voice_levels})` `{total_time}`\n`#{user_rank_xp}` `Score` `({xp_levels})` `{xp}`"
        await ctx.send(profile_message)
    else:
        await  ctx.send("profile not found")
    
#runrunrunrunrun
bot.run('OTY3MTcwODYxNTA3NDQwNjUw.GPLjOD.h93uoLLI57oJBy1whpAZXc7TSBGRiY5QVxNjAo')
