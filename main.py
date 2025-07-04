from flask import Flask, request
import telegram, os, json, time

TOKEN = os.environ.get("BOT_TOKEN", "ISI_TOKEN_BOT")
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

DATA_FILE = "userdata.json"
MINE_COOLDOWN = 8 * 60 * 60  # 8 jam dalam detik
MINE_REWARD = 10

# Load data user dari file
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Simpan data user ke file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route("/", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = str(update.message.chat.id)
    text = update.message.text

    data = load_data()
    if chat_id not in data:
        data[chat_id] = {
            "balance": 0,
            "last_mine": 0,
            "ref": None
        }

    if text == "/start":
        msg = "👋 Selamat datang di Goblin Miners Rush!\n\nKetik /mine untuk mulai menambang GBLN.\nGunakan /invite untuk undang teman dan dapat bonus!\nKetik /help untuk info lengkap."
        bot.send_message(chat_id=chat_id, text=msg)

    elif text == "/help":
        msg = "📜 *Bantuan*\n\n" \
              "/mine – Klaim GBLN setiap 8 jam\n" \
              "/balance – Lihat saldo GBLN kamu\n" \
              "/invite – Dapatkan link referral dan bonus\n" \
              "/start – Mulai ulang bot\n"
        bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

    elif text == "/invite":
        username = update.message.from_user.username or chat_id
        ref_link = f"https://t.me/GoblinMiners_Rush?start={username}"
        msg = f"💌 Ajak teman kamu ke Goblin Miners!\n\nLink kamu: {ref_link}\n\nSetiap teman yang bergabung, kamu dapat +20 GBLN dan 15% dari hasil tambang mereka!"
        bot.send_message(chat_id=chat_id, text=msg)

    elif text == "/balance":
        saldo = data[chat_id]["balance"]
        bot.send_message(chat_id=chat_id, text=f"💰 Saldo kamu: {saldo} GBLN")

    elif text == "/mine":
        now = int(time.time())
        last = data[chat_id]["last_mine"]
        if now - last >= MINE_COOLDOWN:
            data[chat_id]["balance"] += MINE_REWARD
            data[chat_id]["last_mine"] = now
            save_data(data)
            bot.send_message(chat_id=chat_id, text=f"⛏️ Kamu berhasil menambang {MINE_REWARD} GBLN!")
        else:
            remaining = MINE_COOLDOWN - (now - last)
            jam = remaining // 3600
            menit = (remaining % 3600) // 60
            bot.send_message(chat_id=chat_id, text=f"⏳ Kamu harus menunggu {jam} jam {menit} menit sebelum menambang lagi.")

    else:
        bot.send_message(chat_id=chat_id, text="Perintah tidak dikenal. Ketik /help untuk daftar perintah.")

    return "ok"
