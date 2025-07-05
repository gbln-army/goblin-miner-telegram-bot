from flask import Flask, request import telegram import os import json import time

TOKEN = os.environ.get("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE") bot = telegram.Bot(token=TOKEN) app = Flask(name)

DATA_FILE = "userdata.json" MINE_COOLDOWN = 8 * 60 * 60  # 8 hours MINE_REWARD = 10

Load user data

def load_data(): if not os.path.exists(DATA_FILE): return {} with open(DATA_FILE, "r") as f: return json.load(f)

Save user data

def save_data(data): with open(DATA_FILE, "w") as f: json.dump(data, f)

@app.route("/", methods=["POST"]) def webhook(): update = telegram.Update.de_json(request.get_json(force=True), bot) chat_id = str(update.message.chat.id) text = update.message.text

data = load_data()
if chat_id not in data:
    data[chat_id] = {
        "balance": 0,
        "last_mine": 0,
        "ref": None
    }

if text == "/start":
    msg = "\U0001F44B Welcome to Goblin Miners Rush!\n\nType /mine to earn GBLN every 8 hours.\nUse /invite to refer friends and earn bonuses!\nType /help for more commands."
    bot.send_message(chat_id=chat_id, text=msg)

elif text == "/help":
    msg = "\U0001F4D6 *Commands List:*\n\n" \
          "/mine – Mine GBLN every 8 hours\n" \
          "/balance – Check your GBLN balance\n" \
          "/invite – Get your referral link\n" \
          "/start – Restart the bot\n"
    bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

elif text == "/invite":
    username = update.message.from_user.username or chat_id
    ref_link = f"https://t.me/GoblinMiners_Rush?start={username}"
    msg = f"\U0001F48C Invite your friends to Goblin Miners!\n\nYour referral link:\n{ref_link}\n\nYou’ll earn +20 GBLN and 15% of their mining earnings!"
    bot.send_message(chat_id=chat_id, text=msg)

elif text == "/balance":
    balance = data[chat_id]["balance"]
    bot.send_message(chat_id=chat_id, text=f"\U0001F4B0 Your GBLN balance: {balance}")

elif text == "/mine":
    now = int(time.time())
    last = data[chat_id]["last_mine"]
    if now - last >= MINE_COOLDOWN:
        data[chat_id]["balance"] += MINE_REWARD
        data[chat_id]["last_mine"] = now
        save_data(data)
        bot.send_message(chat_id=chat_id, text=f"\u26CF\ufe0f You mined {MINE_REWARD} GBLN!")
    else:
        remaining = MINE_COOLDOWN - (now - last)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        bot.send_message(chat_id=chat_id, text=f"\u23F3 You need to wait {hours}h {minutes}m before mining again.")

else:
    bot.send_message(chat_id=chat_id, text="\u2753 Unknown command. Type /help for available commands.")

return "ok"

if name == "main": app.run(debug=True)

