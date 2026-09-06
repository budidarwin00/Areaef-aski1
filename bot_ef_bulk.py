import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz9hzTgKSYAKp1u39ftbASW4MpM2r4-1M_aWngzoZLSbfl8xYK4VSlo3l-e2xtKHqhM/exec"

MEMBERS = ["Nia","Aditya","Anisa","Aaf","Syarif","Budi","Topik","Yudi","Heru","Dozen","Putri","Arief","Anah","Supriyadi","Zaelani","Eka","Nely"]

def parse_nominal(text: str):
    pattern = r'([\d\.,]+)\s*(k|jt|juta|ribu|rb)?'
    m = re.search(pattern, text.lower())
    if not m:
        return None
    angka_str = m.group(1).replace(',', '.')
    satuan = m.group(2) or ''
    try:
        angka = float(angka_str)
    except:
        return None
    if satuan in ['k','rb','ribu']:
        return int(angka*1000)
    elif satuan in ['jt','juta']:
        return int(angka*1000000)
    else:
        return int(angka)

def send_tx(id_trans, anggota, kategori, desc, nominal):
    payload = {
        "action": "addTransaksi",
        "ID": id_trans,
        "Tanggal": datetime.now().strftime("%Y-%m-%d"),
        "Anggota": anggota,
        "Kategori": f"{kategori} | {desc}",
        "Nominal": nominal
    }
    try:
        requests.post(SCRIPT_URL, json=payload, timeout=15)
        return True
    except:
        return False

def is_bulk(text):
    low = text.lower()
    return any(k in low for k in ["semua", "all", "massal", "iuran semua"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[m for m in MEMBERS[i:i+3]] for i in range(0, len(MEMBERS), 3)]
    keyboard.append(["💧 Iuran Semua 100k", "📊 Saldo"])
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "💧 Bot Kas EF V85 - Bulk Mode ON\n"
        "Web: https://budidarwin00.github.io/Areaef-aski1/\n\n"
        "INPUT SINGLE:\n`Nia 100k iuran`\n`Budi 50k keluar beli galon`\n\n"
        "INPUT MASSAL:\n`iuran semua 100k`\n`semua 100k`\n`massal 50k`\n\n"
        "Akan input 17 anggota sekaligus!",
        reply_markup=markup, parse_mode="Markdown"
    )

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if text == "📊 Saldo":
        try:
            r = requests.get(f"{SCRIPT_URL}?action=getData&t={int(datetime.now().timestamp())}", timeout=10)
            data = r.json()
            trx = data.get('transaksi', [])
            masuk = sum([int(str(x.get('Nominal',0)).replace(',','')) for x in trx if 'Keluar' not in str(x.get('Kategori',''))])
            keluar = sum([int(str(x.get('Nominal',0)).replace(',','')) for x in trx if 'Keluar' in str(x.get('Kategori',''))])
            await update.message.reply_text(f"💰 Saldo: Rp {masuk-keluar:,}\n📥 Masuk: Rp {masuk:,}\n📤 Keluar: Rp {keluar:,}\nTotal {len(trx)} trx")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        return

    if text == "💧 Iuran Semua 100k":
        text = "iuran semua 100k"

    nominal = parse_nominal(text)
    if not nominal:
        await update.message.reply_text("❌ Nominal tidak kebaca. Contoh: `iuran semua 100k` atau `Nia 100k`")
        return

    # BULK MODE
    if is_bulk(text):
        await update.message.reply_text(f"⏳ Proses iuran massal 17 anggota @ Rp {nominal:,}...")
        count = 0
        for anggota in MEMBERS:
            id_trans = f"t{int(datetime.now().timestamp()*1000)}{count}_{anggota}"
            ok = send_tx(id_trans, anggota, "Iuran Bulanan", f"Iuran Bulanan {anggota}", nominal)
            if ok:
                count += 1
        await update.message.reply_text(
            f"✅ Selesai! {count}/17 iuran masuk\n"
            f"💧 Rp {nominal:,} x {count} = Rp {nominal*count:,}\n"
            f"Cek: https://budidarwin00.github.io/Areaef-aski1/"
        )
        return

    # SINGLE MODE
    anggota = None
    for m in MEMBERS:
        if m.lower() in text.lower():
            anggota = m
            break
    if not anggota:
        await update.message.reply_text(f"⚠️ Sebutkan nama. Contoh: `Nia {nominal//1000}k`\nAnggota: {', '.join(MEMBERS)}")
        return

    kategori = "Kas Keluar" if any(x in text.lower() for x in ["keluar","beli","bayar"]) else "Iuran Bulanan" if "iuran" in text.lower() else "Kas Masuk" if "masuk" in text.lower() else "Iuran Bulanan"
    desc = text
    id_trans = f"t{int(datetime.now().timestamp()*1000)}_{anggota}"
    ok = send_tx(id_trans, anggota, kategori, desc, nominal)
    
    if ok:
        await update.message.reply_text(f"✅ {anggota} - Rp {nominal:,} ({kategori})\n{desc}\n→ Masuk ke web GitHub Pages kamu")
    else:
        await update.message.reply_text("❌ Gagal kirim")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    print("Bot Kas EF Bulk running...")
    app.run_polling()

if __name__ == "__main__":
    main()
