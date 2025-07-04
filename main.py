from flask import Flask, request
import json
import time
import os

import telegram
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler

app = Flask(__name__)
BOT_TOKEN = "8113003394:AAEddpjvPAxXu5EE_60xgJ43XqWj7-3bOcw"
bot = telegram.Bot(token=BOT_TOKEN)

DATA_FILE = "data.json"
CLAIM_INTERVAL = 8 * 60 * 60  # 8 jam (detik)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def calculate_level(total_gbln):
    if total_gbln >= 50000:
        return 50
    elif total_gbln >= 25000:
        return 40
    elif total_gbln >= 10000:
        return 30
    elif total_gbln >= 5000:
        return 20
    elif total_gbln >= 2000:
        return 10
    elif total_gbln >= 1000:
        return 5
    elif total_gbln >= 500:
        return 3
    else:
        return 1

def get_claim_amount(level):
    if level >= 50:
        return 50
    elif level >= 30:
        return 30
    elif level >= 10:
        return 20
    else:
        return 10

def start(update, context):
    user = update.effective_user
    data = load_data()
    uid = str(user.id)

    if uid not in data:
        data[uid] = {
            "balance": 0,
            "total_mined": 0,
            "last_claim": 0,
            "referrals": [],
            "ref_by": None
        }

        if context.args:
            ref = context.args[0]
            if ref != uid and ref not in data[uid]["referrals"]:
                data[uid]["ref_by"] = ref
                if ref in data:
                    data[ref]["referrals"].append(uid)
                    data[ref]["balance"] += 20

    save_data(data)
    update.message.reply_text("🟢 Bot Goblin Miner aktif!\nKetik /claim untuk mulai menambang GBLN.")

def claim(update, context):
    user = update.effective_user
    uid = str(user.id)
    data = load_data()

    if uid not in data:
        update.message.reply_text("Ketik /start dulu bro.")
        return

    now = int(time.time())
    last = data[uid]["last_claim"]

    if now - last < CLAIM_INTERVAL:
        remaining = CLAIM_INTERVAL - (now - last)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        update.message.reply_text(f"Tunggu {hours} jam {minutes} menit lagi buat klaim.")
        return

    level = calculate_level(data[uid]["total_mined"])
    amount = get_claim_amount(level)

    data[uid]["balance"] += amount
    data[uid]["total_mined"] += amount
    data[uid]["last_claim"] = now

    # Passive income ke referrer
    ref = data[uid]["ref_by"]
    if ref and ref in data:
        bonus = int(amount * 0.15)
        data[ref]["balance"] += bonus

    save_data(data)
    update.message.reply_text(f"✅ Kamu klaim {amount} GBLN!\nLevel: {level}")

def balance(update, context):
    user = update.effective_user
    uid = str(user.id)
    data = load_data()

    if uid not in data:
        update.message.reply_text("Ketik /start dulu bro.")
        return

    bal = data[uid]["balance"]
    mined = data[uid]["total_mined"]
    level = calculate_level(mined)

    update.message.reply_text(
        f"💰 Balance: {bal} GBLN\n⛏ Total Mining: {mined} GBLN\n🏅 Level: {level}"
    )

def referral(update, context):
    user = update.effective_user
    uid = str(user.id)
    data = load_data()

    if uid not in data:
        update.message.reply_text("Ketik /start dulu bro.")
        return

    update.message.reply_text(
        f"👥 Referral link:\nhttps://t.me/GoblinMiners_Rush?start={uid}\n\n"
        f"🎁 +20 GBLN / teman & 15% passive income!"
    )

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot Goblin Miner jalan!"

from telegram.ext import Dispatcher
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start, pass_args=True))
dispatcher.add_handler(CommandHandler("claim", claim))
dispatcher.add_handler(CommandHandler("balance", balance))
dispatcher.add_handler(CommandHandler("referral", referral))

if __name__ == "__main__":
    app.run(port=10000)
