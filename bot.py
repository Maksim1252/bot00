import asyncio
import json
import os
import time
import random
import math
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery, 
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode

TOKEN = "8028813038:AAHj8WByrS-ftZfcySl9JluramcmaQ393JM"
DATA_FILE = "data.json"
REF_FILE = "referrals.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= ХРАНЕНИЕ =================
def load():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_ref():
    if not os.path.exists(REF_FILE):
        return {}
    with open(REF_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ref():
    with open(REF_FILE, "w", encoding="utf-8") as f:
        json.dump(referrals, f, ensure_ascii=False, indent=2)

users = load()
referrals = load_ref()

# ================= ОСНОВНЫЕ ДАННЫЕ =================
CROPS = {
    "wheat": {"name": "🌾 Пшеница", "time": 300, "seed_price": 15, "yield_min": 2, "yield_max": 4},
    "potato": {"name": "🥔 Картофель", "time": 450, "seed_price": 20, "yield_min": 3, "yield_max": 6},
    "carrot": {"name": "🥕 Морковь", "time": 360, "seed_price": 18, "yield_min": 2, "yield_max": 5},
    "tomato": {"name": "🍅 Помидоры", "time": 600, "seed_price": 25, "yield_min": 1, "yield_max": 3},
    "strawberry": {"name": "🍓 Клубника", "time": 900, "seed_price": 50, "yield_min": 1, "yield_max": 2},
    "mushroom": {"name": "🍄 Грибы", "time": 1200, "seed_price": 40, "yield_min": 1, "yield_max": 3},
    "corn": {"name": "🌽 Кукуруза", "time": 480, "seed_price": 22, "yield_min": 2, "yield_max": 4},
    "cabbage": {"name": "🥬 Капуста", "time": 540, "seed_price": 20, "yield_min": 2, "yield_max": 5},
    "grape": {"name": "🍇 Виноград", "time": 1500, "seed_price": 80, "yield_min": 1, "yield_max": 2},
    "blueberry": {"name": "🫐 Черника", "time": 1800, "seed_price": 100, "yield_min": 1, "yield_max": 2},
}

ANIMALS = {
    "chicken": {"name": "🐔 Курица", "product": "egg", "price": 200, "cooldown": 180, "yield": 1},
    "duck": {"name": "🦆 Утка", "product": "egg", "price": 300, "cooldown": 240, "yield": 1},
    "cow": {"name": "🐄 Корова", "product": "milk", "price": 1500, "cooldown": 600, "yield": 3},
    "goat": {"name": "🐐 Коза", "product": "milk", "price": 1000, "cooldown": 480, "yield": 2},
    "sheep": {"name": "🐑 Овца", "product": "wool", "price": 1200, "cooldown": 1200, "yield": 2},
    "alpaca": {"name": "🦙 Альпака", "product": "wool", "price": 2500, "cooldown": 1800, "yield": 3},
    "pig": {"name": "🐖 Свинья", "product": "meat", "price": 800, "cooldown": 900, "yield": 2},
    "rabbit": {"name": "🐇 Кролик", "product": "meat", "price": 400, "cooldown": 300, "yield": 1},
    "bee": {"name": "🐝 Пчёлы", "product": "honey", "price": 600, "cooldown": 3600, "yield": 5},
    "fish": {"name": "🐟 Рыба", "product": "fish", "price": 500, "cooldown": 7200, "yield": 3},
}

ITEMS = {
    "milk": {"name": "🥛 Молоко", "base": 25},
    "egg": {"name": "🥚 Яйцо", "base": 12},
    "wool": {"name": "🧶 Шерсть", "base": 50},
    "meat": {"name": "🥩 Мясо", "base": 80},
    "honey": {"name": "🍯 Мёд", "base": 60},
    "fish": {"name": "🐟 Рыба", "base": 40},
    "manure": {"name": "💩 Удобрение", "base": 10},
    "cheese": {"name": "🧀 Сыр", "base": 120},
    "bread": {"name": "🍞 Хлеб", "base": 70},
    "fabric": {"name": "🧵 Ткань", "base": 100},
    "jam": {"name": "🍓 Джем", "base": 90},
    "wine": {"name": "🍷 Вино", "base": 200},
    "sausage": {"name": "🌭 Колбаса", "base": 150},
    "butter": {"name": "🧈 Масло", "base": 85},
    "yogurt": {"name": "🥣 Йогурт", "base": 65},
}

# Добавляем товары для каждого растения
for k in CROPS:
    ITEMS[k] = {"name": CROPS[k]["name"], "base": CROPS[k]["seed_price"] * 2 + random.randint(5, 20)}

FACTORIES = {
    "dairy": {"name": "🧀 Молочный завод", "input": "milk", "output": "cheese", "price": 5000, "input_qty": 5, "output_qty": 1},
    "bakery": {"name": "🍞 Пекарня", "input": "wheat", "output": "bread", "price": 4000, "input_qty": 3, "output_qty": 2},
    "textile": {"name": "🧶 Ткацкая фабрика", "input": "wool", "output": "fabric", "price": 6000, "input_qty": 4, "output_qty": 2},
    "butchery": {"name": "🥩 Мясной цех", "input": "meat", "output": "sausage", "price": 5500, "input_qty": 3, "output_qty": 2},
    "winery": {"name": "🍷 Винодельня", "input": "grape", "output": "wine", "price": 8000, "input_qty": 10, "output_qty": 1},
    "jam_factory": {"name": "🍓 Джемовый цех", "input": "strawberry", "output": "jam", "price": 3500, "input_qty": 5, "output_qty": 3},
    "yogurt_factory": {"name": "🥣 Йогуртовый цех", "input": "milk", "output": "yogurt", "price": 4500, "input_qty": 3, "output_qty": 2},
    "butter_factory": {"name": "🧈 Маслобойня", "input": "milk", "output": "butter", "price": 3000, "input_qty": 4, "output_qty": 1},
    "feed_factory": {"name": "🌽 Кормовой цех", "input": "corn", "output": "feed", "price": 2500, "input_qty": 5, "output_qty": 10},
    "fish_processing": {"name": "🐟 Рыбокомбинат", "input": "fish", "output": "fish", "price": 7000, "input_qty": 1, "output_qty": 2},
}

ITEMS["feed"] = {"name": "🌽 Корм", "base": 15}

FIELD_TYPES = {
    "small": {"name": "🪴 Маленькая грядка", "slots": 1, "price": 500, "growth_bonus": 1.0},
    "medium": {"name": "🌿 Средняя грядка", "slots": 3, "price": 2000, "growth_bonus": 1.1},
    "large": {"name": "🌳 Большое поле", "slots": 5, "price": 8000, "growth_bonus": 1.2},
}

VEHICLES = {
    "cart": {"name": "🛒 Телега", "capacity": 100, "speed": 1.0, "price": 1000},
    "truck": {"name": "🚚 Грузовик", "capacity": 500, "speed": 2.0, "price": 10000},
    "tractor": {"name": "🚜 Трактор", "capacity": 300, "speed": 1.5, "price": 15000},
}

# ================= РЫНОК =================
market_prices = {k: ITEMS[k]["base"] for k in ITEMS}
last_price_update = time.time()

def update_prices():
    global last_price_update
    if time.time() - last_price_update > 300:
        for k in market_prices:
            change = random.uniform(0.7, 1.4)
            market_prices[k] = max(5, int(ITEMS[k]["base"] * change))
        last_price_update = time.time()

# ================= ИГРОК =================
def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "money": 1000,
            "storage": {k: 0 for k in ITEMS},
            "fields": [],
            "animals": {k: 0 for k in ANIMALS},
            "vehicles": {k: 0 for k in VEHICLES},
            "factories": {k: 0 for k in FACTORIES},
            "field_types": {"small": 3},
            "stats": {
                "income": 0,
                "tax_paid": 0,
                "items_sold": 0,
                "items_bought": 0,
                "animals_bought": 0,
                "crops_harvested": 0,
                "factories_built": 0,
                "referrals": 0,
                "total_earned": 1000,
                "total_spent": 0,
            },
            "last_collection": {k: 0 for k in ANIMALS},
            "active_transport": None,
            "transport_start": 0,
            "referral_code": f"REF{random.randint(10000, 99999)}",
            "referred_by": None,
        }
        # Создаем начальные поля
        for _ in range(3):
            users[uid]["fields"].append({
                "type": "small",
                "crop": None,
                "planted_at": 0,
            })
    return users[uid]

# ================= ФОРМАТИРОВАНИЕ =================
def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)} сек"
    elif seconds < 3600:
        return f"{int(seconds//60)} мин {int(seconds%60)} сек"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)} час {int(minutes)} мин"

# ================= КЛАВИАТУРЫ =================
def main_menu(user):
    buttons = [
        [InlineKeyboardButton(text=f"💰 Баланс: {user['money']:,}₽", callback_data="balance_info")],
        [InlineKeyboardButton(text="🌱 Ферма", callback_data="farm_menu")],
        [InlineKeyboardButton(text="🐄 Животные", callback_data="animals_menu")],
        [InlineKeyboardButton(text="🏭 Заводы", callback_data="factories_menu")],
        [InlineKeyboardButton(text="🛒 Магазин", callback_data="shop_menu")],
        [InlineKeyboardButton(text="📈 Рынок", callback_data="market_menu")],
        [InlineKeyboardButton(text="🚚 Логистика", callback_data="transport_menu")],
        [InlineKeyboardButton(text="📦 Склад", callback_data="storage_menu")],
        [InlineKeyboardButton(text="🏆 Топ игроков", callback_data="top_players")],
        [InlineKeyboardButton(text="👥 Партнерка", callback_data="referral_menu")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings_menu")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================= КОМАНДЫ =================
@dp.message(CommandStart())
async def start_command(message: Message):
    user = get_user(message.from_user.id)
    save()
    
    await message.answer(
        f"🚜 *Добро пожаловать на Ферму, {message.from_user.first_name}!*\n\n"
        "💰 Стартовый капитал: *1,000₽*\n"
        "🪴 У вас есть 3 грядки\n"
        "🐔 Начните выращивать растения и разводить животных!\n\n"
        "📍 Выберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu(user)
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "📚 *Помощь по игре*\n\n"
        "*Основные команды:*\n"
        "• /start - Начать игру\n"
        "• /help - Справка\n"
        "• /top - Топ игроков\n"
        "• /stats - Ваша статистика\n"
        "• /ref КОД - Ввести реферальный код\n\n"
        "*Игровая механика:*\n"
        "🌱 *Ферма* - выращивайте растения\n"
        "🐄 *Животные* - производят товары\n"
        "🏭 *Заводы* - перерабатывают сырьё\n"
        "🛒 *Рынок* - продавайте товары\n"
        "🚚 *Логистика* - транспорт для доставки\n"
        "👥 *Партнерка* - приглашайте друзей",
        parse_mode=ParseMode.MARKDOWN
    )

@dp.message(Command("top"))
async def top_command(message: Message):
    update_prices()
    
    # Считаем капитал каждого игрока
    player_stats = []
    for uid, user in users.items():
        total = user["money"]
        for item, qty in user["storage"].items():
            total += qty * market_prices.get(item, ITEMS[item]["base"] if item in ITEMS else 10)
        player_stats.append((uid, total, user["stats"]["total_earned"]))
    
    player_stats.sort(key=lambda x: x[1], reverse=True)
    
    top_text = "🏆 *ТОП-10 ИГРОКОВ*\n\n"
    for i, (uid, capital, earned) in enumerate(player_stats[:10], 1):
        try:
            user_info = await bot.get_chat(int(uid))
            name = user_info.first_name or user_info.username or f"Игрок {uid}"
        except:
            name = f"Игрок {uid[:6]}"
        
        medal = ""
        if i == 1: medal = "🥇 "
        elif i == 2: medal = "🥈 "
        elif i == 3: medal = "🥉 "
        
        top_text += f"{medal}*{i}. {name}*\n"
        top_text += f"   💰 Капитал: *{capital:,}₽*\n"
        top_text += f"   📈 Всего заработано: *{earned:,}₽*\n\n"
    
    await message.answer(top_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("stats"))
async def stats_command(message: Message):
    user = get_user(message.from_user.id)
    update_prices()
    
    # Считаем общее богатство
    wealth = user["money"]
    for item, qty in user["storage"].items():
        wealth += qty * market_prices.get(item, ITEMS[item]["base"] if item in ITEMS else 10)
    
    stats_text = (
        f"📊 *Статистика игрока*\n\n"
        f"👤 *{message.from_user.first_name}*\n\n"
        f"💰 *Финансы:*\n"
        f"• Баланс: *{user['money']:,}₽*\n"
        f"• Общее богатство: *{wealth:,}₽*\n"
        f"• Всего заработано: *{user['stats']['total_earned']:,}₽*\n"
        f"• Всего потрачено: *{user['stats']['total_spent']:,}₽*\n"
        f"• Уплачено налогов: *{user['stats']['tax_paid']:,}₽*\n\n"
        f"🌱 *Производство:*\n"
        f"• Собрано урожая: *{user['stats']['crops_harvested']}*\n"
        f"• Куплено животных: *{user['stats']['animals_bought']}*\n"
        f"• Построено заводов: *{user['stats']['factories_built']}*\n"
        f"• Продано товаров: *{user['stats']['items_sold']}*\n"
        f"• Куплено товаров: *{user['stats']['items_bought']}*\n\n"
        f"👥 *Социальное:*\n"
        f"• Приглашено друзей: *{user['stats']['referrals']}*\n"
        f"• Реф. код: *{user['referral_code']}*\n"
    )
    
    await message.answer(stats_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("ref"))
async def ref_command(message: Message):
    user = get_user(message.from_user.id)
    args = message.text.split()
    
    if len(args) > 1:
        ref_code = args[1]
        if ref_code == user["referral_code"]:
            await message.answer("❌ Нельзя использовать свой собственный код!")
            return
        
        if user["referred_by"]:
            await message.answer("❌ Вы уже использовали реферальный код!")
            return
        
        # Ищем реферера
        found = False
        for uid, u in users.items():
            if u.get("referral_code") == ref_code:
                found = True
                user["referred_by"] = ref_code
                user["money"] += 500
                user["stats"]["total_earned"] += 500
                
                u["money"] += 1000
                u["stats"]["total_earned"] += 1000
                u["stats"]["referrals"] += 1
                referrals[uid] = referrals.get(uid, []) + [str(message.from_user.id)]
                
                save()
                save_ref()
                
                await message.answer(
                    "🎉 *Реферальный код активирован!*\n\n"
                    f"💰 Вы получили: *500₽*\n"
                    f"🎁 Реферер получил: *1000₽*\n\n"
                    f"Ваш баланс: *{user['money']:,}₽*",
                    parse_mode=ParseMode.MARKDOWN
                )
                break
        
        if not found:
            await message.answer("❌ Код не найден!")
        return
    
    # Показываем реферальную информацию
    ref_text = (
        "👥 *Партнерская программа*\n\n"
        f"📝 Ваш код: *{user['referral_code']}*\n"
        f"👤 Приглашено: *{user['stats']['referrals']}* друзей\n\n"
        "*Ваша ссылка:*\n"
        f"`https://t.me/{(await bot.get_me()).username}?start=ref{user['referral_code']}`\n\n"
        "*Бонусы:*\n"
        "🎁 За каждого друга: *+1,000₽*\n"
        "💰 Друг получает: *+500₽*\n\n"
        "*Команда:*\n"
        "`/ref КОД` - ввести код друга"
    )
    
    await message.answer(ref_text, parse_mode=ParseMode.MARKDOWN)

# ================= ОБРАБОТЧИКИ КНОПОК =================
@dp.callback_query(F.data == "balance_info")
async def balance_info(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    tax = int(user["money"] * 0.1)
    await callback.message.edit_text(
        f"💰 *Финансы*\n\n"
        f"• Баланс: *{user['money']:,}₽*\n"
        f"• Налог (10%): *{tax:,}₽*\n"
        f"• Всего заработано: *{user['stats']['total_earned']:,}₽*\n"
        f"• Всего потрачено: *{user['stats']['total_spent']:,}₽*\n\n"
        f"💡 Налог взимается ежедневно",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "farm_menu")
async def farm_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    ready = sum(1 for f in user["fields"] if f["crop"] and time.time() > f["planted_at"] + CROPS[f["crop"]]["time"])
    free = sum(1 for f in user["fields"] if not f["crop"])
    
    await callback.message.edit_text(
        f"🌱 *Ферма*\n\n"
        f"🪴 Всего полей: *{len(user['fields'])}*\n"
        f"✅ Готово к сбору: *{ready}*\n"
        f"🟢 Свободных: *{free}*\n\n"
        f"📍 Выберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👨‍🌾 Мои поля", callback_data="my_fields")],
            [InlineKeyboardButton(text="🌱 Посадить", callback_data="plant_crops")],
            [InlineKeyboardButton(text="📦 Собрать урожай", callback_data="harvest_all")],
            [InlineKeyboardButton(text="🏞️ Купить поле", callback_data="buy_fields")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "my_fields")
async def my_fields(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    now = time.time()
    
    text = "🪴 *Мои поля*\n\n"
    for i, field in enumerate(user["fields"], 1):
        text += f"*{i}. {FIELD_TYPES[field['type']]['name']}*\n"
        if field["crop"]:
            crop = CROPS[field["crop"]]
            time_left = (field["planted_at"] + crop["time"]) - now
            if time_left <= 0:
                text += f"   🌾 {crop['name']} - ✅ ГОТОВО\n"
            else:
                text += f"   🌾 {crop['name']} - ⏳ {format_time(time_left)}\n"
        else:
            text += "   🟢 СВОБОДНО\n"
        text += "\n"
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌱 Посадить", callback_data="plant_crops")],
            [InlineKeyboardButton(text="📦 Собрать урожай", callback_data="harvest_all")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="farm_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "plant_crops")
async def plant_crops(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    free = sum(1 for f in user["fields"] if not f["crop"])
    
    if free == 0:
        await callback.answer("❌ Нет свободных полей!", show_alert=True)
        return
    
    buttons = []
    for crop_id, crop in CROPS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{crop['name']} - {crop['seed_price']}₽",
                callback_data=f"plant_{crop_id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="farm_menu")])
    
    await callback.message.edit_text(
        f"🌱 *Посадка растений*\n\n"
        f"🪴 Свободных полей: *{free}*\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите растение:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("plant_"))
async def plant_selected(callback: CallbackQuery):
    crop_id = callback.data.replace("plant_", "")
    user = get_user(callback.from_user.id)
    
    if crop_id not in CROPS:
        await callback.answer("❌ Растение не найдено!", show_alert=True)
        return
    
    crop = CROPS[crop_id]
    
    # Ищем свободное поле
    field_idx = None
    for i, field in enumerate(user["fields"]):
        if not field["crop"]:
            field_idx = i
            break
    
    if field_idx is None:
        await callback.answer("❌ Нет свободных полей!", show_alert=True)
        return
    
    if user["money"] < crop["seed_price"]:
        await callback.answer(f"❌ Не хватает {crop['seed_price'] - user['money']}₽!", show_alert=True)
        return
    
    # Сажаем
    user["fields"][field_idx]["crop"] = crop_id
    user["fields"][field_idx]["planted_at"] = time.time()
    user["money"] -= crop["seed_price"]
    user["stats"]["total_spent"] += crop["seed_price"]
    save()
    
    await callback.answer(f"✅ {crop['name']} посажена!")
    await my_fields(callback)

@dp.callback_query(F.data == "harvest_all")
async def harvest_all(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    now = time.time()
    harvested = 0
    total_value = 0
    
    for field in user["fields"]:
        if field["crop"]:
            crop = CROPS[field["crop"]]
            if now >= field["planted_at"] + crop["time"]:
                # Собираем урожай
                yield_amount = random.randint(crop["yield_min"], crop["yield_max"])
                user["storage"][field["crop"]] += yield_amount
                field["crop"] = None
                harvested += 1
                total_value += yield_amount * market_prices.get(field["crop"], ITEMS[field["crop"]]["base"])
                user["stats"]["crops_harvested"] += yield_amount
    
    if harvested == 0:
        await callback.answer("❌ Нет готового урожая!", show_alert=True)
        return
    
    save()
    await callback.answer(f"✅ Собрано {harvested} полей!")
    await my_fields(callback)

@dp.callback_query(F.data == "buy_fields")
async def buy_fields(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    buttons = []
    for field_id, field in FIELD_TYPES.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{field['name']} - {field['price']}₽",
                callback_data=f"buy_field_{field_id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="farm_menu")])
    
    await callback.message.edit_text(
        f"🏞️ *Покупка полей*\n\n"
        f"🪴 Текущие поля: *{len(user['fields'])}*\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите тип поля:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_field_"))
async def buy_field_selected(callback: CallbackQuery):
    field_id = callback.data.replace("buy_field_", "")
    user = get_user(callback.from_user.id)
    
    if field_id not in FIELD_TYPES:
        await callback.answer("❌ Тип поля не найден!", show_alert=True)
        return
    
    field = FIELD_TYPES[field_id]
    
    if user["money"] < field["price"]:
        await callback.answer(f"❌ Не хватает {field['price'] - user['money']}₽!", show_alert=True)
        return
    
    # Покупаем поле
    user["money"] -= field["price"]
    for _ in range(field["slots"]):
        user["fields"].append({
            "type": field_id,
            "crop": None,
            "planted_at": 0,
        })
    user["stats"]["total_spent"] += field["price"]
    save()
    
    await callback.answer(f"✅ {field['name']} куплен!")
    await buy_fields(callback)

@dp.callback_query(F.data == "animals_menu")
async def animals_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    total_animals = sum(user["animals"].values())
    
    await callback.message.edit_text(
        f"🐄 *Животные*\n\n"
        f"🏠 Всего животных: *{total_animals}*\n"
        f"💰 Стоимость фермы: *{sum(user['animals'][a] * ANIMALS[a]['price'] for a in ANIMALS):,}₽*\n\n"
        f"📍 Выберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Мои животные", callback_data="my_animals")],
            [InlineKeyboardButton(text="🛒 Купить животных", callback_data="buy_animals")],
            [InlineKeyboardButton(text="🥛 Собрать продукцию", callback_data="collect_products")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "my_animals")
async def my_animals(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    now = time.time()
    
    text = "🏠 *Мои животные*\n\n"
    for animal_id, animal in ANIMALS.items():
        count = user["animals"][animal_id]
        if count > 0:
            time_since = now - user["last_collection"][animal_id]
            cycles = int(time_since // animal["cooldown"])
            
            text += f"*{animal['name']}*\n"
            text += f"   🏷️ Количество: *{count}*\n"
            if cycles > 0:
                text += f"   ✅ Можно собрать: *{cycles * count * animal['yield']}*\n"
            else:
                next_time = animal["cooldown"] - time_since
                text += f"   ⏳ Следующий сбор: *{format_time(next_time)}*\n"
            text += "\n"
    
    if text == "🏠 *Мои животные*\n\n":
        text += "❌ У вас нет животных!\n"
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить животных", callback_data="buy_animals")],
            [InlineKeyboardButton(text="🥛 Собрать продукцию", callback_data="collect_products")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="animals_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "buy_animals")
async def buy_animals(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    buttons = []
    for animal_id, animal in ANIMALS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{animal['name']} - {animal['price']}₽",
                callback_data=f"buy_animal_{animal_id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="animals_menu")])
    
    await callback.message.edit_text(
        f"🛒 *Покупка животных*\n\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите животное:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_animal_"))
async def buy_animal_selected(callback: CallbackQuery):
    animal_id = callback.data.replace("buy_animal_", "")
    user = get_user(callback.from_user.id)
    
    if animal_id not in ANIMALS:
        await callback.answer("❌ Животное не найдено!", show_alert=True)
        return
    
    animal = ANIMALS[animal_id]
    
    if user["money"] < animal["price"]:
        await callback.answer(f"❌ Не хватает {animal['price'] - user['money']}₽!", show_alert=True)
        return
    
    user["money"] -= animal["price"]
    user["animals"][animal_id] += 1
    user["stats"]["total_spent"] += animal["price"]
    user["stats"]["animals_bought"] += 1
    save()
    
    await callback.answer(f"✅ {animal['name']} куплен(a)!")
    await my_animals(callback)

@dp.callback_query(F.data == "collect_products")
async def collect_products(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    now = time.time()
    total_collected = 0
    
    for animal_id, animal in ANIMALS.items():
        count = user["animals"][animal_id]
        if count > 0:
            time_since = now - user["last_collection"][animal_id]
            cycles = int(time_since // animal["cooldown"])
            if cycles > 0:
                products = cycles * count * animal["yield"]
                user["storage"][animal["product"]] += products
                user["last_collection"][animal_id] = now
                total_collected += products
    
    if total_collected == 0:
        await callback.answer("❌ Продукция ещё не готова!", show_alert=True)
        return
    
    save()
    await callback.answer(f"✅ Собрано продукции: {total_collected} ед.!")
    await my_animals(callback)

@dp.callback_query(F.data == "factories_menu")
async def factories_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    total_factories = sum(user["factories"].values())
    
    await callback.message.edit_text(
        f"🏭 *Заводы*\n\n"
        f"🏗️ Всего заводов: *{total_factories}*\n"
        f"💰 Инвестиции: *{sum(user['factories'][f] * FACTORIES[f]['price'] for f in FACTORIES):,}₽*\n\n"
        f"📍 Выберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏭 Мои заводы", callback_data="my_factories")],
            [InlineKeyboardButton(text="🔨 Построить завод", callback_data="build_factory")],
            [InlineKeyboardButton(text="⚙️ Произвести товары", callback_data="produce_items")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "my_factories")
async def my_factories(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    text = "🏭 *Мои заводы*\n\n"
    for factory_id, factory in FACTORIES.items():
        count = user["factories"][factory_id]
        if count > 0:
            text += f"*{factory['name']}*\n"
            text += f"   🏷️ Количество: *{count}*\n"
            text += f"   📦 Переработка: *{factory['input_qty']} {ITEMS[factory['input']]['name']} → {factory['output_qty']} {ITEMS[factory['output']]['name']}*\n\n"
    
    if text == "🏭 *Мои заводы*\n\n":
        text += "❌ У вас нет заводов!\n"
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔨 Построить завод", callback_data="build_factory")],
            [InlineKeyboardButton(text="⚙️ Произвести товары", callback_data="produce_items")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="factories_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "build_factory")
async def build_factory(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    buttons = []
    for factory_id, factory in FACTORIES.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{factory['name']} - {factory['price']:,}₽",
                callback_data=f"build_{factory_id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="factories_menu")])
    
    await callback.message.edit_text(
        f"🔨 *Строительство завода*\n\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите тип завода:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("build_"))
async def build_selected(callback: CallbackQuery):
    factory_id = callback.data.replace("build_", "")
    user = get_user(callback.from_user.id)
    
    if factory_id not in FACTORIES:
        await callback.answer("❌ Завод не найден!", show_alert=True)
        return
    
    factory = FACTORIES[factory_id]
    
    if user["money"] < factory["price"]:
        await callback.answer(f"❌ Не хватает {factory['price'] - user['money']:,}₽!", show_alert=True)
        return
    
    user["money"] -= factory["price"]
    user["factories"][factory_id] += 1
    user["stats"]["total_spent"] += factory["price"]
    user["stats"]["factories_built"] += 1
    save()
    
    await callback.answer(f"✅ {factory['name']} построен!")
    await my_factories(callback)

@dp.callback_query(F.data == "produce_items")
async def produce_items(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    buttons = []
    for factory_id, factory in FACTORIES.items():
        count = user["factories"][factory_id]
        if count > 0 and user["storage"].get(factory["input"], 0) >= factory["input_qty"]:
            buttons.append([
                InlineKeyboardButton(
                    text=f"{factory['name']} (Сырьё: {factory['input_qty']})",
                    callback_data=f"produce_{factory_id}"
                )
            ])
    
    if not buttons:
        buttons.append([InlineKeyboardButton(text="❌ Нет доступных заводов", callback_data="noop")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="factories_menu")])
    
    await callback.message.edit_text(
        "⚙️ *Производство товаров*\n\n"
        "📍 Выберите завод для производства:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("produce_"))
async def produce_selected(callback: CallbackQuery):
    factory_id = callback.data.replace("produce_", "")
    user = get_user(callback.from_user.id)
    
    if factory_id not in FACTORIES:
        await callback.answer("❌ Завод не найден!", show_alert=True)
        return
    
    factory = FACTORIES[factory_id]
    
    if user["factories"][factory_id] == 0:
        await callback.answer("❌ У вас нет такого завода!", show_alert=True)
        return
    
    if user["storage"].get(factory["input"], 0) < factory["input_qty"]:
        await callback.answer(f"❌ Не хватает сырья!", show_alert=True)
        return
    
    user["storage"][factory["input"]] -= factory["input_qty"]
    user["storage"][factory["output"]] += factory["output_qty"]
    save()
    
    await callback.answer(f"✅ Произведено {factory['output_qty']} {ITEMS[factory['output']]['name']}!")
    await produce_items(callback)

@dp.callback_query(F.data == "shop_menu")
async def shop_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    await callback.message.edit_text(
        f"🛒 *Магазин*\n\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите категорию:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌱 Семена", callback_data="shop_seeds")],
            [InlineKeyboardButton(text="🐄 Животные", callback_data="shop_animals")],
            [InlineKeyboardButton(text="🚚 Транспорт", callback_data="shop_vehicles")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "shop_seeds")
async def shop_seeds(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    buttons = []
    for crop_id, crop in CROPS.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{crop['name']} - {crop['seed_price']}₽",
                callback_data=f"buy_seed_{crop_id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="shop_menu")])
    
    await callback.message.edit_text(
        f"🌱 *Магазин семян*\n\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите семена:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_seed_"))
async def buy_seed_selected(callback: CallbackQuery):
    crop_id = callback.data.replace("buy_seed_", "")
    user = get_user(callback.from_user.id)
    
    if crop_id not in CROPS:
        await callback.answer("❌ Семена не найдены!", show_alert=True)
        return
    
    crop = CROPS[crop_id]
    
    if user["money"] < crop["seed_price"]:
        await callback.answer(f"❌ Не хватает {crop['seed_price'] - user['money']}₽!", show_alert=True)
        return
    
    # Покупаем семена (добавляем в склад как товар)
    user["money"] -= crop["seed_price"]
    user["storage"][crop_id] = user["storage"].get(crop_id, 0) + 1
    user["stats"]["total_spent"] += crop["seed_price"]
    user["stats"]["items_bought"] += 1
    save()
    
    await callback.answer(f"✅ {crop['name']} куплены!")
    await shop_seeds(callback)

@dp.callback_query(F.data == "shop_vehicles")
async def shop_vehicles(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    buttons = []
    for vehicle_id, vehicle in VEHICLES.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{vehicle['name']} - {vehicle['price']:,}₽",
                callback_data=f"buy_vehicle_{vehicle_id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="shop_menu")])
    
    await callback.message.edit_text(
        f"🚚 *Магазин транспорта*\n\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите транспорт:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_vehicle_"))
async def buy_vehicle_selected(callback: CallbackQuery):
    vehicle_id = callback.data.replace("buy_vehicle_", "")
    user = get_user(callback.from_user.id)
    
    if vehicle_id not in VEHICLES:
        await callback.answer("❌ Транспорт не найден!", show_alert=True)
        return
    
    vehicle = VEHICLES[vehicle_id]
    
    if user["money"] < vehicle["price"]:
        await callback.answer(f"❌ Не хватает {vehicle['price'] - user['money']:,}₽!", show_alert=True)
        return
    
    user["money"] -= vehicle["price"]
    user["vehicles"][vehicle_id] += 1
    user["stats"]["total_spent"] += vehicle["price"]
    save()
    
    await callback.answer(f"✅ {vehicle['name']} куплен!")
    await shop_vehicles(callback)

@dp.callback_query(F.data == "market_menu")
async def market_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    update_prices()
    
    await callback.message.edit_text(
        f"📈 *Рынок*\n\n"
        f"💰 Баланс: *{user['money']:,}₽*\n"
        f"📦 Товаров на складе: *{sum(user['storage'].values())}*\n\n"
        f"📍 Выберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Продать товары", callback_data="sell_items")],
            [InlineKeyboardButton(text="🛒 Купить товары", callback_data="buy_items")],
            [InlineKeyboardButton(text="📉 График цен", callback_data="price_chart")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "sell_items")
async def sell_items(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    update_prices()
    
    buttons = []
    for item_id, item in ITEMS.items():
        count = user["storage"].get(item_id, 0)
        if count > 0:
            price = market_prices[item_id]
            buttons.append([
                InlineKeyboardButton(
                    text=f"{item['name']}: {count} шт × {price}₽",
                    callback_data=f"sell_{item_id}"
                )
            ])
    
    if not buttons:
        buttons.append([InlineKeyboardButton(text="❌ Нет товаров", callback_data="noop")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="market_menu")])
    
    await callback.message.edit_text(
        f"📊 *Продажа товаров*\n\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите товар для продажи:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("sell_"))
async def sell_selected(callback: CallbackQuery):
    item_id = callback.data.replace("sell_", "")
    user = get_user(callback.from_user.id)
    update_prices()
    
    if item_id not in ITEMS:
        await callback.answer("❌ Товар не найден!", show_alert=True)
        return
    
    item = ITEMS[item_id]
    count = user["storage"].get(item_id, 0)
    
    if count == 0:
        await callback.answer("❌ Товара нет на складе!", show_alert=True)
        return
    
    # Продаем все
    price = market_prices[item_id]
    total = count * price
    user["storage"][item_id] = 0
    user["money"] += total
    user["stats"]["total_earned"] += total
    user["stats"]["items_sold"] += count
    
    # Налог с продажи
    tax = int(total * 0.05)
    user["money"] -= tax
    user["stats"]["tax_paid"] += tax
    
    save()
    
    await callback.answer(f"✅ Продано {count} {item['name']} за {total:,}₽!")
    await sell_items(callback)

@dp.callback_query(F.data == "price_chart")
async def price_chart(callback: CallbackQuery):
    update_prices()
    
    text = "📉 *Цены на рынке*\n\n"
    for item_id, item in list(ITEMS.items())[:10]:
        base = ITEMS[item_id]["base"]
        current = market_prices[item_id]
        change = ((current - base) / base) * 100
        
        arrow = "➡️"
        if change > 0:
            arrow = "📈"
        elif change < 0:
            arrow = "📉"
        
        text += f"{arrow} *{item['name']}*\n"
        text += f"   Цена: *{current}₽* (база: {base}₽)\n"
        text += f"   Изменение: *{change:+.1f}%*\n\n"
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить цены", callback_data="price_chart")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="market_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "transport_menu")
async def transport_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    total_vehicles = sum(user["vehicles"].values())
    
    await callback.message.edit_text(
        f"🚚 *Логистика*\n\n"
        f"🚛 Всего транспорта: *{total_vehicles}*\n"
        f"⚡ Общая грузоподъемность: *{sum(user['vehicles'][v] * VEHICLES[v]['capacity'] for v in VEHICLES):,}*\n\n"
        f"📍 Выберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚛 Мой транспорт", callback_data="my_transport")],
            [InlineKeyboardButton(text="📦 Отправить груз", callback_data="send_cargo")],
            [InlineKeyboardButton(text="🛒 Магазин транспорта", callback_data="shop_vehicles")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "my_transport")
async def my_transport(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    text = "🚛 *Мой транспорт*\n\n"
    for vehicle_id, vehicle in VEHICLES.items():
        count = user["vehicles"][vehicle_id]
        if count > 0:
            text += f"*{vehicle['name']}*\n"
            text += f"   🏷️ Количество: *{count}*\n"
            text += f"   📦 Вместимость: *{vehicle['capacity']}*\n"
            text += f"   ⚡ Скорость: *{vehicle['speed']}x*\n\n"
    
    if text == "🚛 *Мой транспорт*\n\n":
        text += "❌ У вас нет транспорта!\n"
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить транспорт", callback_data="shop_vehicles")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="transport_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "send_cargo")
async def send_cargo(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    if sum(user["vehicles"].values()) == 0:
        await callback.answer("❌ У вас нет транспорта!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📦 *Отправка груза*\n\n"
        "🚛 Выберите транспорт для отправки:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Телега (100 единиц)", callback_data="send_cart")],
            [InlineKeyboardButton(text="🚚 Грузовик (500 единиц)", callback_data="send_truck")],
            [InlineKeyboardButton(text="🚜 Трактор (300 единиц)", callback_data="send_tractor")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="transport_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "send_cart")
async def send_cart(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    if user["vehicles"]["cart"] == 0:
        await callback.answer("❌ У вас нет телег!", show_alert=True)
        return
    
    # Отправляем груз
    user["money"] += 500  # Доход за доставку
    user["stats"]["total_earned"] += 500
    save()
    
    await callback.answer("✅ Груз отправлен! Доход: +500₽")
    await transport_menu(callback)

@dp.callback_query(F.data == "storage_menu")
async def storage_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    # Показываем топ 10 товаров по количеству
    items_sorted = sorted(user["storage"].items(), key=lambda x: x[1], reverse=True)[:10]
    
    text = "📦 *Склад*\n\n"
    total_items = sum(user["storage"].values())
    text += f"📊 Всего товаров: *{total_items}*\n\n"
    
    for item_id, count in items_sorted:
        if count > 0:
            item_name = ITEMS[item_id]["name"] if item_id in ITEMS else item_id
            text += f"• {item_name}: *{count}* шт.\n"
    
    if total_items == 0:
        text += "❌ Склад пуст!\n"
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="storage_menu")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "top_players")
async def top_players(callback: CallbackQuery):
    # Считаем капитал каждого игрока
    player_stats = []
    for uid, user in users.items():
        total = user["money"]
        for item, qty in user["storage"].items():
            total += qty * market_prices.get(item, ITEMS[item]["base"] if item in ITEMS else 10)
        player_stats.append((uid, total, user["stats"]["total_earned"]))
    
    player_stats.sort(key=lambda x: x[1], reverse=True)
    
    text = "🏆 *ТОП-10 ИГРОКОВ*\n\n"
    for i, (uid, capital, earned) in enumerate(player_stats[:10], 1):
        medal = ""
        if i == 1: medal = "🥇 "
        elif i == 2: medal = "🥈 "
        elif i == 3: medal = "🥉 "
        
        try:
            user_info = await bot.get_chat(int(uid))
            name = user_info.first_name or user_info.username or f"Игрок {uid[:4]}"
        except:
            name = f"Игрок {uid[:4]}"
        
        text += f"{medal}*{i}. {name}*\n"
        text += f"   💰 Капитал: *{capital:,}₽*\n"
        text += f"   📈 Заработано: *{earned:,}₽*\n\n"
    
    if not player_stats:
        text += "❌ Пока нет игроков!\n"
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="top_players")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "referral_menu")
async def referral_menu(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    await callback.message.edit_text(
        f"👥 *Партнерская программа*\n\n"
        f"📝 Ваш код: *{user['referral_code']}*\n"
        f"👤 Приглашено: *{user['stats']['referrals']}*\n\n"
        f"*Ваша ссылка:*\n"
        f"`https://t.me/{(await bot.get_me()).username}?start=ref{user['referral_code']}`\n\n"
        f"*Бонусы:*\n"
        f"🎁 За каждого друга: *+1,000₽*\n"
        f"💰 Друг получает: *+500₽*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Скопировать ссылку", callback_data="copy_ref")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "copy_ref")
async def copy_ref(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    await callback.answer(f"Ссылка скопирована: https://t.me/{(await bot.get_me()).username}?start=ref{user['referral_code']}")

@dp.callback_query(F.data == "settings_menu")
async def settings_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙️ *Настройки*\n\n"
        "📍 Выберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats_info")],
            [InlineKeyboardButton(text="🔄 Сбросить игру", callback_data="reset_game")],
            [InlineKeyboardButton(text="ℹ️ О игре", callback_data="about_game")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "stats_info")
async def stats_info(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    
    await callback.message.edit_text(
        f"📊 *Ваша статистика*\n\n"
        f"💰 Финансы:\n"
        f"• Баланс: *{user['money']:,}₽*\n"
        f"• Заработано всего: *{user['stats']['total_earned']:,}₽*\n"
        f"• Потрачено всего: *{user['stats']['total_spent']:,}₽*\n\n"
        f"🌱 Производство:\n"
        f"• Собрано урожая: *{user['stats']['crops_harvested']}*\n"
        f"• Куплено животных: *{user['stats']['animals_bought']}*\n"
        f"• Построено заводов: *{user['stats']['factories_built']}*\n\n"
        f"📦 Торговля:\n"
        f"• Продано товаров: *{user['stats']['items_sold']}*\n"
        f"• Куплено товаров: *{user['stats']['items_bought']}*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "reset_game")
async def reset_game(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔄 *Сброс игры*\n\n"
        "⚠️ Вы уверены, что хотите сбросить всю игру?\n"
        "Все ваши данные будут удалены без возможности восстановления!\n\n"
        "Это действие нельзя отменить!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, сбросить игру", callback_data="confirm_reset")],
            [InlineKeyboardButton(text="❌ Нет, отменить", callback_data="settings_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "confirm_reset")
async def confirm_reset(callback: CallbackQuery):
    uid = str(callback.from_user.id)
    if uid in users:
        # Сохраняем только статистику о рефералах
        referrals_count = users[uid]["stats"]["referrals"]
        ref_code = users[uid]["referral_code"]
        
        # Создаем нового пользователя
        users[uid] = {
            "money": 1000,
            "storage": {k: 0 for k in ITEMS},
            "fields": [],
            "animals": {k: 0 for k in ANIMALS},
            "vehicles": {k: 0 for k in VEHICLES},
            "factories": {k: 0 for k in FACTORIES},
            "field_types": {"small": 3},
            "stats": {
                "income": 0,
                "tax_paid": 0,
                "items_sold": 0,
                "items_bought": 0,
                "animals_bought": 0,
                "crops_harvested": 0,
                "factories_built": 0,
                "referrals": referrals_count,
                "total_earned": 1000,
                "total_spent": 0,
            },
            "last_collection": {k: 0 for k in ANIMALS},
            "active_transport": None,
            "transport_start": 0,
            "referral_code": ref_code,
            "referred_by": users[uid].get("referred_by", None),
        }
        # Создаем начальные поля
        for _ in range(3):
            users[uid]["fields"].append({
                "type": "small",
                "crop": None,
                "planted_at": 0,
            })
        save()
    
    await callback.answer("✅ Игра сброшена! Начните заново.")
    await start_command(callback.message)

@dp.callback_query(F.data == "about_game")
async def about_game(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ *О игре*\n\n"
        "🚜 *Фермерский симулятор*\n"
        "Версия: 2.0\n\n"
        "📱 *Описание:*\n"
        "Симулятор фермерского хозяйства с полным циклом производства:\n"
        "• Выращивание растений\n"
        "• Разведение животных\n"
        "• Производство на заводах\n"
        "• Торговля на рынке\n"
        "• Логистика и транспорт\n\n"
        "👨‍🌾 *Разработчик:*\n"
        "Telegram бот для развлечения и обучения\n\n"
        "📞 *Поддержка:*\n"
        "По вопросам работы бота обращайтесь к разработчику",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "help_menu")
async def help_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "❓ *Помощь*\n\n"
        "*Основные разделы:*\n"
        "🌱 *Ферма* - выращивайте растения на полях\n"
        "🐄 *Животные* - производят товары автоматически\n"
        "🏭 *Заводы* - перерабатывают сырьё в товары\n"
        "🛒 *Магазин* - покупайте семена и транспорт\n"
        "📈 *Рынок* - продавайте товары по рыночным ценам\n"
        "🚚 *Логистика* - транспорт для доставки товаров\n"
        "📦 *Склад* - хранилище ваших товаров\n"
        "👥 *Партнерка* - приглашайте друзей за бонусы\n\n"
        "*Советы:*\n"
        "1. Начинайте с быстрых культур (пшеница)\n"
        "2. Разнообразьте производство\n"
        "3. Следите за ценами на рынке\n"
        "4. Приглашайте друзей за бонусы",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Команды", callback_data="show_commands")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "show_commands")
async def show_commands(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 *Список команд*\n\n"
        "*/start* - Начать игру\n"
        "*/help* - Показать справку\n"
        "*/top* - Топ игроков\n"
        "*/stats* - Ваша статистика\n"
        "*/ref КОД* - Ввести реферальный код\n\n"
        "*Пример:*\n"
        "`/ref REF12345`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="help_menu")]
        ])
    )
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"🚜 *Главное меню Фермы*\n\n"
        f"👋 Добро пожаловать, {callback.from_user.first_name}!\n"
        f"💰 Баланс: *{user['money']:,}₽*\n\n"
        f"📍 Выберите раздел:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu(user)
    )
    await callback.answer()

@dp.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()

# ================= ФОНОВЫЕ ЗАДАЧИ =================
async def passive_income():
    """Пассивный доход от животных"""
    while True:
        for uid, user in users.items():
            now = time.time()
            for animal_id, animal in ANIMALS.items():
                count = user["animals"][animal_id]
                if count > 0:
                    time_since = now - user["last_collection"][animal_id]
                    cycles = int(time_since // animal["cooldown"])
                    if cycles > 0:
                        products = cycles * count * animal["yield"]
                        user["storage"][animal["product"]] += products
                        user["last_collection"][animal_id] = now
        
        save()
        await asyncio.sleep(60)

async def tax_collection():
    """Сбор налогов"""
    while True:
        for uid, user in users.items():
            tax = int(user["money"] * 0.1)  # 10% налог
            if tax > 0 and user["money"] >= tax:
                user["money"] -= tax
                user["stats"]["tax_paid"] += tax
        
        save()
        await asyncio.sleep(3600)  # Каждый час

# ================= ЗАПУСК =================
async def main():
    print("🚜 Фермерский симулятор запущен!")
    asyncio.create_task(passive_income())
    asyncio.create_task(tax_collection())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
