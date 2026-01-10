import asyncio
import json
import os
import time
import random
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.filters import Command

# ================= НАСТРОЙКИ =================
TOKEN = "7793884650:AAEn4qshUrLom8-f68LemIa1sKM-liqhPus"
ADMIN_ID = 1807082571

DATA_FILE = "data.json"
PROMO_FILE = "promos.json"
SEASON_FILE = "season.json"

WORK_REWARD = 1
REF_OWNER = 500
REF_FRIEND = 250
TAX_PERCENT = 5
SERVICE_FEE = 10
SEASON_DURATION = 7 * 24 * 60 * 60  # 7 дней

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
}

# ================= ФАЙЛЫ =================
def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load(DATA_FILE, {})
promos = load(PROMO_FILE, {})
season = load(SEASON_FILE, {"start": time.time()})

def save_all():
    save(DATA_FILE, users)
    save(PROMO_FILE, promos)
    save(SEASON_FILE, season)

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
            "waiting": None,
            "used_promos": []
        }
    return users[uid]

def income(u):
    return sum(u["business"][k] * BUSINESSES[k][2] for k in BUSINESSES)

# ================= СЕЗОН =================
def check_season():
    if time.time() - season["start"] >= SEASON_DURATION:
        season["start"] = time.time()
        for u in users.values():
            u["money"] = 0
            u["bank"]["balance"] = 0
        save_all()

# ================= МЕНЮ =================
def menu(uid=0):
    kb = [
        [InlineKeyboardButton(text="💰 Работать", callback_data="work")],
        [InlineKeyboardButton(text="🏢 Бизнесы", callback_data="business")],
        [InlineKeyboardButton(text="🏦 Банк", callback_data="bank")],
        [InlineKeyboardButton(text="🎁 Бонус", callback_data="bonus")],
        [InlineKeyboardButton(text="📦 Кейсы", callback_data="cases")],
        [InlineKeyboardButton(text="🎟 Промокоды", callback_data="promo")],
        [InlineKeyboardButton(text="🏆 ТОП", callback_data="top")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")]
    ]
    if uid == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="🛠 Админ", callback_data="admin")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ================= START =================
@dp.message(Command("start"))
async def start(msg: Message):
    check_season()
    get_user(msg.from_user.id, msg.from_user.username)

    args = msg.text.split()
    if len(args) > 1:
        ref = args[1]
        u = users[str(msg.from_user.id)]
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
    check_season()
    u = get_user(call.from_user.id)

    # ===== БИЗНЕСЫ =====
    if call.data == "business":
        text = "🏢 Бизнесы:\n\n"
        kb = []
        for k, (name, price, _) in BUSINESSES.items():
            text += f"{name}: {u['business'][k]} шт\n"
            kb.append([InlineKeyboardButton(text=f"Купить {name} ({price}₽)", callback_data=f"buy_{k}")])
        kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
        await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        return await call.answer()

    if call.data.startswith("buy_"):
        k = call.data.replace("buy_", "")
        price = BUSINESSES[k][1]
        if u["money"] >= price:
            u["money"] -= price
            u["business"][k] += 1
            save_all()
            await call.message.edit_text("✅ Бизнес куплен", reply_markup=menu(call.from_user.id))
        else:
            await call.message.edit_text("❌ Не хватает денег", reply_markup=menu(call.from_user.id))
        return await call.answer()

    # ===== БАНК =====
    if call.data == "bank":
        bank = u["bank"]
        if not bank["opened"]:
            kb = [
                [InlineKeyboardButton(text="🆕 Открыть счёт", callback_data="bank_open")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
            ]
            await call.message.edit_text("🏦 Счёт не открыт", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        else:
            kb = [
                [InlineKeyboardButton(text="➕ Внести", callback_data="bank_deposit")],
                [InlineKeyboardButton(text="➖ Снять", callback_data="bank_withdraw")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
            ]
            await call.message.edit_text(f"🏦 Баланс: {bank['balance']}₽", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        return await call.answer()

    if call.data == "bank_open":
        u["bank"]["opened"] = True
        save_all()
        await call.message.edit_text("✅ Счёт открыт", reply_markup=menu(call.from_user.id))
        return await call.answer()

    # ===== БОНУС =====
    if call.data == "bonus":
        me = await bot.get_me()
        await call.message.edit_text(
            f"🎁 Бонус\n\n🤝 Пригласи друга:\nhttps://t.me/{me.username}?start={call.from_user.id}\n\n"
            f"Ты: +{REF_OWNER}₽\nДруг: +{REF_FRIEND}₽",
            reply_markup=menu(call.from_user.id)
        )
        return await call.answer()

    # ===== КЕЙСЫ =====
    if call.data == "cases":
        kb = [
            [InlineKeyboardButton(text="🎁 Кейс (100₽)", callback_data="case_normal")],
            [InlineKeyboardButton(text="🏆 Сезонный кейс (300₽)", callback_data="case_season")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ]
        await call.message.edit_text("📦 Кейсы", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        return await call.answer()

    if call.data.startswith("case_"):
        price = 100 if call.data == "case_normal" else 300
        if u["money"] < price:
            return await call.answer("❌ Недостаточно денег", show_alert=True)

        u["money"] -= price
        if random.random() < 0.5:
            u["money"] += 200
            text = "💰 Выпало 200₽"
        else:
            biz = random.choice(list(BUSINESSES.keys()))
            u["business"][biz] += 1
            text = f"🏢 Выпал бизнес: {BUSINESSES[biz][0]}"
        save_all()
        await call.message.edit_text(text, reply_markup=menu(call.from_user.id))
        return await call.answer()

    # ===== ПРОМОКОДЫ =====
    if call.data == "promo":
        u["waiting"] = "promo"
        await call.message.edit_text("🎟 Введи промокод", reply_markup=menu(call.from_user.id))
        return await call.answer()

    # ===== АДМИН =====
    if call.data == "admin" and call.from_user.id == ADMIN_ID:
        kb = [
            [InlineKeyboardButton(text="🎟 Создать промокод", callback_data="admin_promo")],
            [InlineKeyboardButton(text="🏁 Новый сезон", callback_data="admin_season")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ]
        await call.message.edit_text("🛠 Админ-панель", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
        return await call.answer()

    if call.data == "admin_season" and call.from_user.id == ADMIN_ID:
        season["start"] = time.time()
        for u2 in users.values():
            u2["money"] = 0
            u2["bank"]["balance"] = 0
        save_all()
        await call.message.edit_text("🏁 Новый сезон начат", reply_markup=menu(call.from_user.id))
        return await call.answer()

    if call.data == "admin_promo" and call.from_user.id == ADMIN_ID:
        u["waiting"] = "admin_promo"
        await call.message.edit_text(
            "Формат:\nКОД money СУММА ЛИМИТ\nКОД business КЛЮЧ ЛИМИТ",
            reply_markup=menu(call.from_user.id)
        )
        return await call.answer()

    # ===== ОСТАЛЬНОЕ =====
    if call.data == "work":
        u["money"] += WORK_REWARD
        await call.message.edit_text(f"+{WORK_REWARD}₽", reply_markup=menu(call.from_user.id))

    elif call.data == "profile":
        await call.message.edit_text(
            f"👤 {u['nick']}\n💰 {u['money']}₽\n🏢 Доход: {income(u)}₽/мин",
            reply_markup=menu(call.from_user.id)
        )

    elif call.data == "top":
        top = sorted(users.values(), key=lambda x: x["money"], reverse=True)[:10]
        txt = "🏆 ТОП:\n" + "\n".join(f"{i+1}. {x['nick']} — {x['money']}₽" for i, x in enumerate(top))
        await call.message.edit_text(txt, reply_markup=menu(call.from_user.id))

    elif call.data == "back":
        await call.message.edit_text("Главное меню", reply_markup=menu(call.from_user.id))

    save_all()
    await call.answer()

# ================= ТЕКСТ =================
@dp.message()
async def text_input(msg: Message):
    u = get_user(msg.from_user.id)
    try:
        if u["waiting"] == "admin_promo" and msg.from_user.id == ADMIN_ID:
            p = msg.text.split()
            promos[p[0].upper()] = {"type": p[1], "value": p[2], "limit": int(p[3]), "used": 0}
            u["waiting"] = None
            save_all()
            return await msg.answer("✅ Промокод создан", reply_markup=menu(msg.from_user.id))

        if u["waiting"] == "promo":
            code = msg.text.upper()
            u["waiting"] = None
            if code in promos and promos[code]["used"] < promos[code]["limit"] and code not in u["used_promos"]:
                promo = promos[code]
                if promo["type"] == "money":
                    u["money"] += int(promo["value"])
                elif promo["type"] == "business":
                    u["business"][promo["value"]] += 1
                promo["used"] += 1
                u["used_promos"].append(code)
                save_all()
                return await msg.answer("🎉 Промокод активирован", reply_markup=menu(msg.from_user.id))
            return await msg.answer("❌ Промокод недоступен", reply_markup=menu(msg.from_user.id))
    except:
        u["waiting"] = None
        await msg.answer("❌ Ошибка")

# ================= ПАССИВ =================
async def passive():
    while True:
        check_season()
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


