import discord
from discord.ext import commands, tasks
import sqlite3
from datetime import datetime, timedelta
import random

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Database Setup
db = sqlite3.connect("bot_database.db")
cursor = db.cursor()

# Table Initialization
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE,
    balance INTEGER DEFAULT 1000,
    exp INTEGER DEFAULT 0,
    inventory TEXT DEFAULT '',
    loan INTEGER DEFAULT 0,
    last_attendance TEXT DEFAULT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    name TEXT PRIMARY KEY,
    price INTEGER,
    volatility REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS market_properties (
    name TEXT PRIMARY KEY,
    price INTEGER,
    quantity INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_properties (
    user_id INTEGER,
    property_name TEXT,
    quantity INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    PRIMARY KEY(user_id, property_name)
)
""")

# Initialize properties in the market
items = [
    ("은", 100, 0.01),
    ("금", 100, 0.01),
    ("백금", 1000, 0.01),
    ("투슬코인", 10000, 1.00)
]

market_properties = [
    ("투슬시 땅", 1000000, 10),
    ("투슬 APT", 3000000, 12),
    ("주택", 2000000, 50)
]
cursor.executemany("INSERT OR IGNORE INTO market_properties (name, price, quantity) VALUES (?, ?, ?)", market_properties)
db.commit()

# Helper Functions
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def create_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    db.commit()

def get_market_properties():
    cursor.execute("SELECT name, price, quantity FROM market_properties")
    return cursor.fetchall()

def update_user_property(user_id, property_name, quantity):
    cursor.execute("""
        INSERT INTO user_properties (user_id, property_name, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, property_name) DO UPDATE SET quantity = quantity + ?
    """, (user_id, property_name, quantity, quantity))
    db.commit()

def get_user_properties(user_id):
    cursor.execute("SELECT property_name, quantity FROM user_properties WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Commands
@bot.command()
async def 부동산시세(ctx):
    properties = get_market_properties()
    message = "🏠 현재 부동산 시세:\n"
    for name, price, quantity in properties:
        message += f"- {name}: {price}원 (수량: {quantity})\n"
    await ctx.send(message)

@bot.command()
async def 부동산구매(ctx, property_name: str, quantity: int):
    if quantity <= 0:
        await ctx.send("올바른 수량을 입력해주세요.")
        return

    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    cursor.execute("SELECT price, quantity FROM market_properties WHERE name = ?", (property_name,))
    property_data = cursor.fetchone()

    if not property_data:
        await ctx.send("존재하지 않는 부동산입니다.")
        return

    price, market_quantity = property_data
    total_price = price * quantity

    if market_quantity < quantity:
        await ctx.send("시장에 해당 부동산의 수량이 부족합니다.")
        return

    if user[2] < total_price:
        await ctx.send("잔액이 부족합니다.")
        return

    # Update market and user data
    cursor.execute("UPDATE market_properties SET quantity = quantity - ? WHERE name = ?", (quantity, property_name))
    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (total_price, ctx.author.id))
    update_user_property(ctx.author.id, property_name, quantity)

    await ctx.send(f"{ctx.author.mention}님이 {property_name} {quantity}개를 구매했습니다. (총액: {total_price}원)")

@bot.command()
async def 부동산판매(ctx, property_name: str, quantity: int):
    if quantity <= 0:
        await ctx.send("올바른 수량을 입력해주세요.")
        return

    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    cursor.execute("SELECT quantity FROM user_properties WHERE user_id = ? AND property_name = ?", (ctx.author.id, property_name))
    user_property = cursor.fetchone()

    if not user_property or user_property[0] < quantity:
        await ctx.send("판매할 수량이 부족합니다.")
        return

    cursor.execute("SELECT price FROM market_properties WHERE name = ?", (property_name,))
    market_property = cursor.fetchone()

    if not market_property:
        await ctx.send("존재하지 않는 부동산입니다.")
        return

    price = market_property[0]
    total_price = price * quantity

    # Update market and user data
    cursor.execute("UPDATE market_properties SET quantity = quantity + ? WHERE name = ?", (quantity, property_name))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (total_price, ctx.author.id))
    cursor.execute("UPDATE user_properties SET quantity = quantity - ? WHERE user_id = ? AND property_name = ?", (quantity, ctx.author.id, property_name))

    await ctx.send(f"{ctx.author.mention}님이 {property_name} {quantity}개를 판매했습니다. (총액: {total_price}원)")

@bot.command()
async def 내부동산(ctx):
    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    user_properties = get_user_properties(ctx.author.id)
    if not user_properties:
        await ctx.send(f"{ctx.author.mention}님은 현재 소유한 부동산이 없습니다.")
        return

    message = f"🏠 {ctx.author.mention}님의 부동산 목록:\n"
    for property_name, quantity in user_properties:
        message += f"- {property_name}: {quantity}개\n"

    await ctx.send(message)


@bot.command()
async def 등록(ctx):
    create_user(ctx.author.id)
    await ctx.send(f"{ctx.author.mention} 등록되었습니다.")

@bot.command()
async def 잔액(ctx):
    user = get_user(ctx.author.id)
    if user:
        await ctx.send(f"{ctx.author.mention}님의 잔액은 {user[2]}원입니다.")
    else:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")

@bot.command()
async def 출석(ctx):
    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    last_attendance = user[6]
    now = datetime.now()

    if last_attendance:
        last_attendance_time = datetime.strptime(last_attendance, "%Y-%m-%d %H:%M:%S")
        if now - last_attendance_time < timedelta(hours=24):
            remaining_time = timedelta(hours=24) - (now - last_attendance_time)
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"출석 보상은 아직 받을 수 없습니다. 남은 시간: {hours}시간 {minutes}분 {seconds}초")
            return

    cursor.execute("UPDATE users SET balance = balance + 500, last_attendance = ? WHERE user_id = ?", (now.strftime("%Y-%m-%d %H:%M:%S"), ctx.author.id))
    db.commit()
    await ctx.send(f"{ctx.author.mention} 출석 보상으로 500원을 받았습니다!")

@bot.command()
async def 도박(ctx, amount: int):
    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    if amount <= 0 or amount > user[2]:
        await ctx.send("올바른 금액을 입력해주세요.")
        return

    if random.choice([True, False]):
        winnings = amount * 2
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (winnings, ctx.author.id))
        db.commit()
        await ctx.send(f"🎉 {ctx.author.mention} 도박에 성공하여 {winnings}원을 얻었습니다!")
    else:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, ctx.author.id))
        db.commit()
        await ctx.send(f"💸 {ctx.author.mention} 도박에 실패하여 {amount}원을 잃었습니다.")

# 3분마다 가격을 업데이트하는 주기적 작업
@tasks.loop(minutes=3)
async def update_item_prices_task():
    update_item_prices()

@bot.command()
async def 시세확인(ctx):
    try:
        item_prices = get_item_prices()  # 데이터베이스에서 시세 가져옴
        message = "📈 현재 아이템 시세:\n"
        for name, price in item_prices:
            message += f"- {name}: {price}원\n"
        await ctx.send(message)
    except Exception as e:
        print(f"Error in 시세확인: {e}")
        await ctx.send("시세 확인 중 오류가 발생했습니다. 나중에 다시 시도해주세요.")



@bot.command()
async def 초기화(ctx):
    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    last_attendance = user[6]
    now = datetime.now()

    if last_attendance:
        last_reset = datetime.strptime(last_attendance, "%Y-%m-%d %H:%M:%S")
        if now - last_reset < timedelta(weeks=1):
            remaining_time = timedelta(weeks=1) - (now - last_reset)
            days, seconds = remaining_time.days, remaining_time.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            await ctx.send(f"초기화는 1주일 쿨타임이 있습니다. 남은 시간: {days}일 {hours}시간 {minutes}분")
            return

    cursor.execute("DELETE FROM users WHERE user_id = ?", (ctx.author.id,))
    cursor.execute("DELETE FROM user_properties WHERE user_id = ?", (ctx.author.id,))
    cursor.execute("INSERT INTO users (user_id, last_attendance) VALUES (?, ?)", (ctx.author.id, now.strftime("%Y-%m-%d %H:%M:%S")))
    db.commit()
    await ctx.send(f"{ctx.author.mention}님의 데이터가 초기화되었습니다.")

@bot.command()
async def 돈랭킹(ctx):
    cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    rankings = cursor.fetchall()
    message = "💰 돈 랭킹:\n"
    for i, (user_id, balance) in enumerate(rankings, start=1):
        user = await bot.fetch_user(user_id)
        message += f"{i}. {user.name}: {balance}원\n"
    await ctx.send(message)

@bot.command()
async def EXP랭킹(ctx):
    cursor.execute("SELECT user_id, exp FROM users ORDER BY exp DESC LIMIT 10")
    rankings = cursor.fetchall()
    message = "🌟 경험치 랭킹:\n"
    for i, (user_id, exp) in enumerate(rankings, start=1):
        user = await bot.fetch_user(user_id)
        message += f"{i}. {user.name}: {exp} EXP\n"
    await ctx.send(message)
    
@bot.command()
async def 대출(ctx, amount: int):
    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    # 이미 대출을 받은 경우
    if user['loan'] > 0:
        await ctx.send(f"{ctx.author.mention} 이미 대출을 받으셨습니다. 재대출은 불가능합니다.")
        return

    if amount <= 0:
        await ctx.send("올바른 금액을 입력해주세요.")
        return

    cursor.execute("UPDATE users SET balance = balance + ?, loan = loan + ? WHERE user_id = ?", (amount, amount, ctx.author.id))
    db.commit()
    await ctx.send(f"{ctx.author.mention} {amount}원을 대출했습니다. (상환 금액: {amount * 1.5}원)")

@bot.command()
async def 상환(ctx):
    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    loan = user[5]
    if loan <= 0:
        await ctx.send("상환할 대출이 없습니다.")
        return

    repayment = int(loan * 1.5)
    if user[2] < repayment:
        await ctx.send("잔액이 부족하여 상환할 수 없습니다.")
        return

    cursor.execute("UPDATE users SET balance = balance - ?, loan = 0 WHERE user_id = ?", (repayment, ctx.author.id))
    db.commit()
    await ctx.send(f"{ctx.author.mention}님의 대출을 상환했습니다. (상환 금액: {repayment}원)")

@bot.command()
async def 송금(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("올바른 금액을 입력해주세요.")
        return

    sender = get_user(ctx.author.id)
    receiver = get_user(member.id)

    if not sender:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    if not receiver:
        await ctx.send(f"{member.mention}님은 등록되지 않았습니다.")
        return

    if sender[2] < amount:
        await ctx.send("잔액이 부족합니다.")
        return

    cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, ctx.author.id))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member.id))
    db.commit()
    await ctx.send(f"{ctx.author.mention}님이 {member.mention}님에게 {amount}원을 송금했습니다.")

@bot.command()
async def 구입(ctx, item_name: str, quantity: int):
    if quantity <= 0:
        await ctx.send("올바른 수량을 입력해주세요.")
        return

    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    cursor.execute("SELECT price FROM items WHERE name = ?", (item_name,))
    item = cursor.fetchone()

    if not item:
        await ctx.send("존재하지 않는 아이템입니다.")
        return

    total_price = item[0] * quantity
    if user[2] < total_price:
        await ctx.send("잔액이 부족합니다.")
        return

    cursor.execute("UPDATE users SET balance = balance - ?, inventory = inventory || ? || ',' WHERE user_id = ?", (total_price, f"{item_name}x{quantity}", ctx.author.id))
    db.commit()
    await ctx.send(f"{ctx.author.mention}님이 {item_name} {quantity}개를 구매했습니다. (총액: {total_price}원)")

@bot.command()
async def 판매(ctx, item_name: str, quantity: int):
    if quantity <= 0:
        await ctx.send("올바른 수량을 입력해주세요.")
        return

    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    inventory = user[4].split(',') if user[4] else []
    item_key = f"{item_name}x{quantity}"

    if item_key not in inventory:
        await ctx.send("인벤토리에 해당 아이템이 부족합니다.")
        return

    cursor.execute("SELECT price FROM items WHERE name = ?", (item_name,))
    item = cursor.fetchone()

    if not item:
        await ctx.send("존재하지 않는 아이템입니다.")
        return

    total_price = item[0] * quantity
    inventory.remove(item_key)
    updated_inventory = ','.join(inventory)
    cursor.execute("UPDATE users SET balance = balance + ?, inventory = ? WHERE user_id = ?", (total_price, updated_inventory, ctx.author.id))
    db.commit()
    await ctx.send(f"{ctx.author.mention}님이 {item_name} {quantity}개를 판매했습니다. (총액: {total_price}원)")

@bot.command()
async def 인벤토리(ctx):
    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    inventory = user[4]
    if not inventory or inventory.strip() == "":
        await ctx.send(f"{ctx.author.mention}님의 인벤토리가 비어 있습니다.")
        return

    item_list = inventory.split(',')
    item_summary = {}

    for item in item_list:
        if "x" in item:
            name, count = item.split('x')
            item_summary[name] = item_summary.get(name, 0) + int(count)

    message = f"📦 {ctx.author.mention}님의 인벤토리:\n"
    for name, count in item_summary.items():
        message += f"- {name}: {count}개\n"

    await ctx.send(message)



def add_exp(user_id, amount):
    cursor.execute("SELECT exp FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        return False

    new_exp = user[0] + amount
    cursor.execute("UPDATE users SET exp = ? WHERE user_id = ?", (new_exp, user_id))
    db.commit()

    # 레벨 계산
    level = calculate_level(new_exp)
    return level

def calculate_level(exp):
    # 간단한 레벨 공식: exp = 100 * level^2
    level = 1
    while exp >= 100 * (level ** 2):
        level += 1
    return level - 1




@bot.command()
async def 레벨(ctx):
    user = get_user(ctx.author.id)
    if not user:
        await ctx.send("먼저 !등록 명령어로 등록해주세요.")
        return

    exp = user[3]  # EXP 값
    level = calculate_level(exp)
    await ctx.send(f"{ctx.author.mention}님의 현재 레벨은 {level}이고, 경험치는 {exp}입니다.")


@bot.event
async def on_message(message):
    if message.author.bot:  # 봇의 메시지는 무시
        return

    user = get_user(message.author.id)
    if not user:
        create_user(message.author.id)  # 유저 등록
        user = get_user(message.author.id)

    # EXP 상승 (메시지마다 10 EXP 증가)
    cursor.execute("UPDATE users SET exp = exp + 10 WHERE user_id = ?", (message.author.id,))
    db.commit()

    # 레벨업 조건 (예: EXP가 100의 배수일 때 레벨업)
    exp = user[3] + 10  # 현재 EXP + 증가한 EXP
    if exp % 100 == 0:
        await message.channel.send(f"🎉 {message.author.mention}님이 레벨업했습니다! 현재 EXP: {exp}")

    await bot.process_commands(message)  # 명령어 처리

    
bot.run("설마 토큰을 볼려고여기까지 내려온건아니겠지")

