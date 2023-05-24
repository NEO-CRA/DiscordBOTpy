import asyncio
import discord
from discord.ext import commands
from getpass import getpass
import mysql.connector
import hashlib
import contextlib

intents = discord.Intents.all()

discordnamecheck = ""

bot = commands.Bot(command_prefix='!', intents=intents)

config = {
    'host': '',
    'database': '',
    'user': '',
    'password': ''
}

def channel_check(channel_id):
    def predicate(ctx):
        return ctx.message.channel.id == channel_id
    return commands.check(predicate)

def checkdiscord(discordname):
    global discordnamecheck
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        print(discordname)
        query = "SELECT discordhash FROM users WHERE discordhash = %s"
        values = (discordname,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        if result:
            print(f"Retry Registration/False")
            return True
        else:
            print("New Registration/True")
            return False
    except Exception as e:
        print(f"Error adding data to database: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def add_to_database(name, password_hash, discordhash, password):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        query = "SELECT nickname FROM users WHERE nickname = %s"
        values = (name,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        if result:
            print(f"Nickname {name} already exists in the database")
            return False
        else:
            query = "INSERT INTO users (nickname, userpassword, discordhash, userpasswordnonhash) VALUES (%s, %s, %s, %s)"
            values = (name, password_hash, discordhash, password)
            cursor.execute(query, values)
            connection.commit()
            print(f"Data added to database: {name}, {password_hash}, {discordhash}, {password}")
            return True
    except Exception as e:
        print(f"Error adding data to database: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def replace_to_database(password, passwordhash, discord):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        query = "SELECT discordhash FROM users WHERE discordhash = %s"
        values = (discord,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        query = "UPDATE users SET userpasswordnonhash=%s, userpassword=%s WHERE discordhash=%s"
        values = (password, passwordhash, discord)
        cursor.execute(query, values)
        connection.commit()
        print(f"Data added to database: {password}")
        return True
    except Exception as e:
        print(f"Error adding data to database: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    while True:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game("!register/!login/!repass"))
        await asyncio.sleep(60)
        await bot.change_presence(status=discord.Status.online, activity=discord.Game("Версия V1.3"))
        await asyncio.sleep(10)


@bot.command()
@channel_check(1074651964555661412)
async def register(ctx):
    await ctx.message.delete()
    discordname = ctx.author.mention
    discordhash = ctx.author.mention
    member = ctx.author
    add_role = discord.utils.get(ctx.guild.roles, name='Игрок')
    rem_role = discord.utils.get(ctx.guild.roles, name='Бич')
    print(checkdiscord(discordname))
    if not checkdiscord(discordname) == True:

        print("Регистрация" + ctx.author.mention)
        start_mes = await  ctx.author.send("Для начала регистрации, вы должны подтвердить(поставить голочку) что вы прочитали правила и знаете как пользоватся ботом")
        await start_mes.add_reaction('\u2705')

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '\u2705'

        try:
            reaction = await bot.wait_for('reaction_add', check=check_reaction, timeout=60.0)
        except asyncio.TimeoutError:
            await  ctx.author.channel.send('Время ожидания реакции истекло.')

        await  ctx.author.send(f"``Привет ``{ctx.author.mention}``! Введи данные для регистрации``")
        await  ctx.author.send(f"``Имя:``")

        def check(m):
            return m.author == ctx.author

        msg = await bot.wait_for('message', check=check)
        name = msg.content
        await  ctx.author.send(f"``Пароль:``")

        def check(m):
            return m.author == ctx.author

        msg = await bot.wait_for('message', check=check)
        password = msg.content
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        while not add_to_database(name, password_hash, discordhash, password):
            await  ctx.author.send(f"``Извините, но имя {name} уже занято или вы использовали запрещенные символы(Кирилицу). Пожалуйста, выберите другое имя.``")
            msg = await bot.wait_for('message', check=check)
            name = msg.content

        reg_msg = await  ctx.author.send(f"``Спасибо за регистрацию, ``{ctx.author.mention}``!")

        embed = discord.Embed(title="Скачивание и Установка",
                              description=":)",
                              color=discord.Color.blue())
        embed.add_field(name="1.Скачивание и установка JDK 17",
                        value="Скачайте JDK 17(https://download.oracle.com/java/17/archive/jdk-17.0.7_windows-x64_bin.exe) и установите его. ВАЖНО - перезагрузите ваш компьютер",
                        inline=False)
        embed.add_field(name="2.Скачивание и установка INTERMINE launcher",
                        value="Скачайте INTERMINE launcher (https://cdn.discordapp.com/attachments/1074567857939152968/1102215240428564480/Launcher.exe) и поместите его в удобное для вас место.",
                        inline=False)
        embed.add_field(name="3.Запуск INTERMINE launcher",
                        value="Запустите INTERMINE launcher и наслаждайтесь игрой на сервере.",
                        inline=False)
        await  ctx.author.send(embed=embed)

    elif not checkdiscord(discordname) == False:
        await ctx.author.send("``Вы уже зарегестрировали аккаунт.``")

@bot.command()
@channel_check(1074651964555661412)
async def login(ctx):
    await ctx.message.delete()
    discordname = ctx.author.mention
    print(discordname)
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print('Connected to MySQL database')
            cursor = connection.cursor()
            query = 'SELECT discordhash FROM users WHERE discordhash = %s'
            values = (discordname,)
            cursor.execute(query, values)
            result = cursor.fetchall()

            if result:
                Nick = 'SELECT nickname FROM users WHERE discordhash = %s'
                values = (discordname,)  
                cursor.execute(Nick, values)
                resultNick = cursor.fetchall() 

                Pass = 'SELECT userpasswordnonhash FROM users WHERE discordhash = %s'
                cursor.execute(Pass, values)
                resultPass = cursor.fetchall() 

                print(resultPass, resultNick)
                await ctx.author.send("Ваши данные:")
                await ctx.author.send(resultNick)
                await ctx.author.send(resultPass)
                await ctx.author.send("https://cdn.discordapp.com/attachments/1074567857939152968/1102215240428564480/Launcher.exe")
                connection.close()
            else:
                await ctx.author.send("Вы не зарегестрировали аккаунт")
                connection.close()
        else:
            print('Failed to connect to MySQL database')
    except mysql.connector.Error as error:
        print('Error connecting to MySQL database:', error)
    finally:
        if connection.is_connected():
            connection.close()
            print('MySQL database connection closed')

@bot.command()
@channel_check(1074651964555661412)
async def renpass(ctx):
    await ctx.message.delete()
    discordname = ctx.author.mention
    print(discordname)
    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            print('Connected to MySQL database')
            cursor = connection.cursor()
            query = 'SELECT discordhash FROM users WHERE discordhash = %s'
            values = (discordname,)
            cursor.execute(query, values)
            result = cursor.fetchall()

            if result:

                await ctx.author.send("Введи пароль на который хотите сменить:")

                def check(m):
                    return m.author == ctx.author

                msg = await bot.wait_for('message', check=check)
                password = msg.content
                passwordhash = hashlib.sha256(password.encode()).hexdigest()
                replace_to_database(password, passwordhash, discordname)
                await ctx.author.send("Пороль изменён")
            else:
                await ctx.author.send("Вы не зарегестрировали аккаунт")
                connection.close()
        else:
            print('Failed to connect to MySQL database')
    except mysql.connector.Error as error:
        print('Error connecting to MySQL database:', error)
    finally:
        if connection.is_connected():
            connection.close()
            print('MySQL database connection closed')




bot.run('')
