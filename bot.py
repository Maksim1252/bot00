import asyncio
import json
import os
import time
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.filters import Command

# ================= НАСТРОЙКИ =================
TOKEN = "7793884650:AAEn4qshUrLom8-f68LemIa1sKM-liqhPus"
ADMIN_ID = 1807082571
DATA_FILE = "data.json"
PROMO_FILE = "promos.json"

WORK_REWARD = 1
REF_OWNER = 500
REF_FRIEND = 250
TAX_PERCENT = 5
SERVICE_FEE = 10

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= БИЗНЕСЫ =================
BUSINESSES = {
    "shop": ("🏪 Ларёк", 10, 1),
    "market": ("🛒 Магазин", 30, 3),
    "bakery": ("🥖 Пекарня", 80, 8),
    "cafe": ("☕ Кафе", 150, 15),
    "bar": ("🍺 Бар", 300, 30),
    "restaurant": ("🍽 Ресторан", 700, 80),
    "factory": ("🏭 Завод", 1500, 180),
    "logistics": ("🚚 Логистика", 3000, 400),
    "bankbiz": ("🏦 Банк", 6000, 900),
    "it": ("💻 IT", 12000, 1800),
    "media": ("📺 Медиа", 25000, 4000),
    "pharma": ("💊 Фарма", 50000, 9000),
    "energy": ("⚡ Энергия", 100000, 20000),
    "oil": ("🛢 Нефть", 250000, 55000),
    "holding": ("🏙 Холдинг", 500000, 120000),
    "space": ("🛰 Космос", 1_000_000, 300000),
    "ai": ("🤖 AI", 2_500_000, 800000),
    "quantum": ("⚛️ Квант", 5_000_000, 1_800_000),
    "metaverse": ("🌐 Метавселенная", 10_000_000, 4_000_000),
    "galactic": ("🌌 Галактика", 25_000_000, 12_000_000),
}

# ================= ДАННЫЕ =================
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_json(DATA_FILE, {})
promos = load_json(PROMO_FILE, {})

def save_all():
    save_json(DATA_FILE, users)
    save_json(PROMO_FILE, promos)

# ================= ИГРОК =================
def get_user(uid, username=""):
    uid = str(uid)
    if uid not in users:
        users[uid] = {
            "nick": username or f"Игрок{uid[-4:]}",
            "money": 0,
            "business": {k: 0 for k in BUSINESSES},
            "bank": {"opened": False, "balance": 0},
            "refs": 0,
            "referred_by": None,
            "last_work": 0,
            "waiting": None,
            "used_promos": []
        }
    return users[uid]

def income(u):
    return sum(u["business"][k] * BUSINESSES[k][2] for k in BUSINESSES)

# ================= МЕНЮ =================
def menu(uid=0):
    kb = [
        [InlineKeyboardButton(text="💰 Работать", callback_data="work")],
        [InlineKeyboardButton(text="🏢 Бизнесы", callback_data="business")],
        [InlineKeyboardButton(text="🏦 Банк", callback_data="bank")],
        [InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus")],
        [InlineKeyboardButton(text="🎟 Промокоды", callback_data="promo")],
        [InlineKeyboardButton(text="🏆 ТОП", callback_data="top")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")]
    ]
    if uid == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="🛠 Админ-панель", callback_data="admin")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ================= START =================
@dp.message(Command("start"))
async def start(msg: Message):
    args = msg.text.split()
    u = get_user(msg.from_user.id, msg.from_user.username)

    if len(args) > 1:
        ref = args[1]
        if ref in users and ref != str(msg.from_user.id) and u["referred_by"] is None:
            u["referred_by"] = ref
            users[ref]["money"] += REF_OWNER
            users[ref]["refs"] += 1
            u["money"] += REF_FRIEND

    save_all()
    await msg.answer("🎮 Бизнес-игра запущена", reply_markup=menu(msg.from_user.id))

# ================= CALLBACKS =================
@dp.callback_query()
async def cb(call: CallbackQuery):
    u = get_user(call.from_user.id)

    # ---------- АДМИН ----------
    if call.data == "admin" and call.from_user.id == ADMIN_ID:
        kb = [
            [InlineKeyboardButton(text="🎟 Создать промокод", callback_data="admin_promo")],
            [InlineKeyboardButton(text="👥 Игроки", callback_data="admin_users")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ]
        await call.message.edit_text("🛠 Админ-панель", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

    elif call.data == "admin_promo" and call.from_user.id == ADMIN_ID:
        u["waiting"] = "admin_promo"
        await call.message.edit_text(
            "🎟 Создание промокода\n\n"
            "Формат:\n"
            "КОД money СУММА ЛИМИТ\n"
            "КОД business КЛЮЧ_БИЗНЕСА ЛИМИТ\n\n"
            "Пример:\n"
            "START money 1000 50\n"
            "BIZ business cafe 10",
            reply_markup=menu(call.from_user.id)
        )

    elif call.data == "admin_users" and call.from_user.id == ADMIN_ID:
        text = "👥 Игроки:\n\n"
        for uid, usr in users.items():
            text += f"{usr['nick']} | ID {uid} | 💰 {usr['money']}₽\n"
        await call.message.edit_text(text[:4096], reply_markup=menu(call.from_user.id))

    # ---------- ПРОМО ----------
    elif call.data == "promo":
        u["waiting"] = "promo"
        await call.message.edit_text("🎟 Введи промокод сообщением", reply_markup=menu(call.from_user.id))

    elif call.data == "back":
        await call.message.edit_text("Главное меню", reply_markup=menu(call.from_user.id))

    save_all()
    await call.answer()

# ================= ВВОД ТЕКСТА =================
@dp.message()
async def text_input(msg: Message):
    u = get_user(msg.from_user.id)

    try:
        # --- админ создаёт промокод ---
        if u["waiting"] == "admin_promo" and msg.from_user.id == ADMIN_ID:
            p = msg.text.split()
            code = p[0].upper()
            ptype = p[1]
            value = p[2]
            limit = int(p[3])

            promos[code] = {
                "type": ptype,
                "value": value,
                "limit": limit,
                "used": 0
            }

            u["waiting"] = None
            save_all()
            await msg.answer(f"✅ Промокод {code} создан", reply_markup=menu(msg.from_user.id))

        # --- игрок активирует промокод ---
        elif u["waiting"] == "promo":
            code = msg.text.upper()
            u["waiting"] = None

            if code not in promos:
                await msg.answer("❌ Промокод не найден", reply_markup=menu(msg.from_user.id))
                return
            if promos[code]["used"] >= promos[code]["limit"]:
                await msg.answer("⛔ Лимит исчерпан", reply_markup=menu(msg.from_user.id))
                return
            if code in u["used_promos"]:
                await msg.answer("⛔ Уже использован", reply_markup=menu(msg.from_user.id))
                return

            promo = promos[code]
            if promo["type"] == "money":
                u["money"] += int(promo["value"])
            elif promo["type"] == "business" and promo["value"] in u["business"]:
                u["business"][promo["value"]] += 1

            promo["used"] += 1
            u["used_promos"].append(code)
            save_all()
            await msg.answer("🎉 Промокод активирован!", reply_markup=menu(msg.from_user.id))

    except:
        u["waiting"] = None
        await msg.answer("❌ Ошибка ввода", reply_markup=menu(msg.from_user.id))

# ================= PASSIVE =================
async def passive():
    while True:
        for u in users.values():
            inc = income(u)
            tax = inc * TAX_PERCENT // 100
            service = sum(u["business"].values()) * SERVICE_FEE
            u["money"] += max(0, inc - tax - service)
        save_all()
        await asyncio.sleep(60)

# ================= RUN =================
async def main():
    asyncio.create_task(passive())
    await dp.start_polling(bot)

asyncio.run(main())
