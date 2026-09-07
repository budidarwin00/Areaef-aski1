"""
Telegram Bot Kas EF V86 - TELEGRAM + 17 ANGGOTA + SHEET + WEB + EXCEL
Sheet: https://docs.google.com/spreadsheets/d/1nFDwsS_ot4KLwacMcmW9alRR-DsZ48pqM3shx_fSZ0g/edit
Web: https://budidarwin00.github.io/Areaef-aski1/
17 Anggota: Nia, Aditya, Anisa, Aaf, Syarif, Budi, Topik, Yudi, Heru, Dozen, Putri, Arief, Anah, Supriyadi, Zaelani, Nely, Eka

Fitur ALL 1,2,3:
1. Telegram -> Web Auto-Sync via Apps Script
2. Edit/Hapus di Web V86
3. 17 Anggota Support

Install:
pip install python-telegram-bot pandas openpyxl gspread oauth2client requests
"""

import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("TOKEN") or "GANTI_DENGAN_TOKEN_BOTFATHER_KAMU"

# === CONFIG V86 - SUDAH TERHUBUNG KE SHEET KAMU ===
GOOGLE_SHEET_ID = "1nFDwsS_ot4KLwacMcmW9alRR-DsZ48pqM3shx_fSZ0g"
GOOGLE_CREDS_FILE = "creds.json"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz9hzTgKSYAKp1u39ftbASW4MpM2r4-1M_aWngzoZLSbfl8xYK4VSlo3l-e2xtKHqhM/exec"
APPS_SCRIPT_URL_OLD = "https://script.google.com/macros/s/AKfycbyoaoGAxT_MkGtcqX-V1_SHMKD4OzUARJuiHUGca0fo-GJPQocuL_f2w8NEMGPorVNgIQ/exec"

ANGGOTA_LIST = ["Nia","Aditya","Anisa","Aaf","Syarif","Budi","Topik","Yudi","Heru","Dozen","Putri","Arief","Anah","Supriyadi","Zaelani","Nely","Eka"]

def sync_to_gsheet_via_appscript(anggota, kategori, nominal, keterangan):
    """Feature 1: Telegram -> Web Auto-Sync"""
    try:
        import requests
        payload = {
            "action": "addTransaksi",
            "ID": f"TG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "Tanggal": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Anggota": anggota,
            "Kategori": f"{kategori} | {keterangan}",
            "Nominal": nominal
        }
        for url in [APPS_SCRIPT_URL, APPS_SCRIPT_URL_OLD]:
            try:
                r = requests.post(url, json=payload, timeout=10)
                print(f"Apps Script sync {url[:50]}: {r.status_code}")
                if r.status_code == 200:
                    return True
            except Exception as e:
                print(f"Sync try {url[:30]} failed: {e}")
                continue
        return False
    except Exception as e:
        print(f"Apps Script error: {e}")
        return False

def sync_to_gsheet(id_, tipe, jumlah, ket, tanggal, user_id, anggota_name="Telegram"):
    """Backup via gspread"""
    if not GOOGLE_SHEET_ID or not os.path.exists(GOOGLE_CREDS_FILE):
        return
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("Transaksi")
        kategori = "Kas Masuk" if tipe=="MASUK" else "Kas Keluar"
        trx_id = f"TG-{id_}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        tgl_format = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        admin = f"Telegram-{anggota_name}"
        sheet.append_row([trx_id, tgl_format, anggota_name, kategori, jumlah, ket, "", admin])
        print(f"GSheet direct: {trx_id}")
    except Exception as e:
        print(f"GSheet direct skip (pakai Apps Script aja): {e}")

conn = sqlite3.connect("kas.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS transaksi (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, tipe TEXT, jumlah INTEGER, keterangan TEXT, tanggal TEXT)")
conn.commit()

def format_rp(n):
    return f"Rp {n:,}".replace(",", ".")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    anggota_str = ", ".join(ANGGOTA_LIST[:7]) + f" ... total {len(ANGGOTA_LIST)} anggota"
    text = f"""
💰 *Bot Kas EF V86 - PT Astra Komponen Indonesia*
🌐 Web: budidarwin00.github.io/Areaef-aski1/
📊 Sheet: Database Kas Real (17 anggota)

*Perintah V86:*
 /tambah - Tambah transaksi
  Contoh: /tambah MASUK 100000 Nia iuran bulanan
  Contoh: /tambah KELUAR 20000 Budi beli gula
  Format: /tambah TIPE JUMLAH [ANGGOTA] KETERANGAN

 /anggota - Lihat 17 anggota
 /web - Link web V86 + Sheet
 /list - Lihat 10 transaksi terakhir
 /saldo - Cek saldo
 /hapus <id> - Hapus transaksi
 /edit <id> - Edit transaksi
 /laporan - Laporan bulan ini
 /excel - Export Excel

Anggota: {anggota_str}
Tipe: MASUK / KELUAR
"""
    await update.message.reply_text(text, parse_mode="Markdown")

async def anggota_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👥 *17 Anggota Kas EF V86:*

" + "\n".join([f"{i}. {n}" for i,n in enumerate(ANGGOTA_LIST,1)]) + "\n\nPakai: /tambah MASUK 100000 Nia iuran\nBot auto-detect nama anggota!"
    await update.message.reply_text(text, parse_mode="Markdown")

async def web_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🌐 *Web Kas EF V86 TELEGRAM+CRUD*
"
        f"https://budidarwin00.github.io/Areaef-aski1/

"
        f"📊 *Sheet Database Kas Real*
"
        f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit

"
        f"🤖 *Flow:* Telegram -> Sheet -> Web (auto-sync)
"
        f"✏️ Web bisa Edit/Hapus langsung (Feature 2)",
        parse_mode="Markdown"
    )

async def tambah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text("Format:\n/tambah MASUK 100000 [ANGGOTA] keterangan\nContoh:\n/tambah MASUK 100000 Nia iuran bulanan\n/tambah KELUAR 20000 Budi beli gula")
            return
        tipe = args[0].upper()
        if tipe not in ["MASUK", "KELUAR"]:
            await update.message.reply_text("Tipe harus MASUK atau KELUAR")
            return
        jumlah = int(args[1].replace(".","").replace(",","").replace("k","000").replace("K","000"))
        anggota_input = args[2]
        anggota_detected = next((a for a in ANGGOTA_LIST if a.lower()==anggota_input.lower()), None)
        if anggota_detected:
            anggota_name = anggota_detected
            keterangan = " ".join(args[3:]) if len(args)>3 else f"Iuran {anggota_name}"
        else:
            anggota_name = update.effective_user.first_name or "Telegram"
            keterangan = " ".join(args[2:])

        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M")
        kategori = "Kas Masuk" if tipe=="MASUK" else "Kas Keluar"

        cur.execute("INSERT INTO transaksi (user_id, tipe, jumlah, keterangan, tanggal) VALUES (?,?,?,?,?)",
                    (update.effective_user.id, tipe, jumlah, f"{anggota_name}: {keterangan}", tanggal))
        conn.commit()
        id_baru = cur.lastrowid

        # Feature 1: Sync via Apps Script -> Web auto-update
        sync_to_gsheet_via_appscript(anggota_name, kategori, jumlah, keterangan)
        sync_to_gsheet(id_baru, tipe, jumlah, keterangan, tanggal, update.effective_user.id, anggota_name)

        await update.message.reply_text(
            f"✅ *V86 Ditambahkan!*\n"
            f"ID: {id_baru}\n"
            f"👤 Anggota: {anggota_name}\n"
            f"{tipe} {format_rp(jumlah)}\n"
            f"📝 {keterangan}\n"
            f"🌐 Web & Sheet auto-update!\n"
            f"https://budidarwin00.github.io/Areaef-aski1/",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}\nFormat: /tambah MASUK 100000 Nia iuran")

async def list_transaksi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur.execute("SELECT id, tipe, jumlah, keterangan, tanggal FROM transaksi WHERE user_id=? ORDER BY id DESC LIMIT 10", (update.effective_user.id,))
    rows = cur.fetchall()
    if not rows:
        await update.message.reply_text("Belum ada transaksi.")
        return
    text = "📒 *10 Transaksi Terakhir V86:*\n\n"
    for r in rows:
        id_, tipe, jumlah, ket, tgl = r
        emoji = "🟢" if tipe=="MASUK" else "🔴"
        text += f"{emoji} ID {id_} | {tipe} {format_rp(jumlah)}\n   {ket} - {tgl[:10]}\n"
    text += "\nGunakan /hapus <id> atau /edit <id> ...\nEdit juga bisa di Web V86!"
    keyboard = []
    for r in rows[:5]:
        id_ = r[0]
        keyboard.append([InlineKeyboardButton(f"Hapus ID {id_}", callback_data=f"hapus_{id_}"),
                         InlineKeyboardButton(f"Edit ID {id_}", callback_data=f"edit_{id_}")])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur.execute("SELECT SUM(jumlah) FROM transaksi WHERE user_id=? AND tipe='MASUK'", (update.effective_user.id,))
    masuk = cur.fetchone()[0] or 0
    cur.execute("SELECT SUM(jumlah) FROM transaksi WHERE user_id=? AND tipe='KELUAR'", (update.effective_user.id,))
    keluar = cur.fetchone()[0] or 0
    saldo_ = masuk - keluar
    text = f"💵 *Saldo Kas V86*\n\nMasuk : {format_rp(masuk)}\nKeluar: {format_rp(keluar)}\n-------------------\nSaldo : {format_rp(saldo_)}\n\n17 Anggota: {', '.join(ANGGOTA_LIST)}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def hapus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        id_hapus = int(context.args[0])
        cur.execute("DELETE FROM transaksi WHERE id=? AND user_id=?", (id_hapus, update.effective_user.id))
        conn.commit()
        if cur.rowcount:
            await update.message.reply_text(f"🗑️ Transaksi ID {id_hapus} dihapus. Hapus juga di Web V86 & Sheet.")
        else:
            await update.message.reply_text("ID tidak ditemukan.")
    except:
        await update.message.reply_text("Format: /hapus 3")

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 4:
            await update.message.reply_text("Format: /edit ID MASUK/KELUAR JUMLAH KETERANGAN\nContoh: /edit 3 MASUK 60000 Nia iuran")
            return
        id_edit = int(args[0])
        tipe = args[1].upper()
        jumlah = int(args[2].replace(".", ""))
        ket = " ".join(args[3:])
        cur.execute("UPDATE transaksi SET tipe=?, jumlah=?, keterangan=? WHERE id=? AND user_id=?",
                    (tipe, jumlah, ket, id_edit, update.effective_user.id))
        conn.commit()
        if cur.rowcount:
            await update.message.reply_text(f"✏️ ID {id_edit} diupdate: {tipe} {format_rp(jumlah)} - {ket}\nEdit juga bisa di Web V86!")
        else:
            await update.message.reply_text("ID tidak ditemukan.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bulan = datetime.now().strftime("%Y-%m")
    cur.execute("SELECT tipe, jumlah FROM transaksi WHERE user_id=? AND tanggal LIKE ?", (update.effective_user.id, f"{bulan}%"))
    rows = cur.fetchall()
    masuk = sum(r[1] for r in rows if r[0]=="MASUK")
    keluar = sum(r[1] for r in rows if r[0]=="KELUAR")
    await update.message.reply_text(f"📊 Laporan {bulan} - V86\nMasuk: {format_rp(masuk)}\nKeluar: {format_rp(keluar)}\nSaldo: {format_rp(masuk-keluar)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("hapus_"):
        id_ = int(data.split("_")[1])
        cur.execute("DELETE FROM transaksi WHERE id=? AND user_id=?", (id_, query.from_user.id))
        conn.commit()
        await query.edit_message_text(f"🗑️ ID {id_} dihapus. Ketik /list untuk refresh. Hapus juga di Web V86.")
    elif data.startswith("edit_"):
        id_ = int(data.split("_")[1])
        await query.edit_message_text(f"Untuk edit ID {id_}, ketik:\n/edit {id_} MASUK 100000 Nia keterangan baru\nAtau edit langsung di Web V86!")

async def export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import pandas as pd
    import os
    cur.execute("SELECT id, tipe, jumlah, keterangan, tanggal FROM transaksi WHERE user_id=? ORDER BY id ASC", (update.effective_user.id,))
    rows = cur.fetchall()
    if not rows:
        await update.message.reply_text("Belum ada data untuk export.")
        return
    df = pd.DataFrame(rows, columns=["ID","Tipe","Jumlah","Keterangan","Tanggal"])
    saldo = 0
    saldos = []
    for _, tipe, jumlah, _, _ in rows:
        if tipe=="MASUK":
            saldo += jumlah
        else:
            saldo -= jumlah
        saldos.append(saldo)
    df["Saldo"] = saldos
    filename = f"/tmp/kas_{update.effective_user.id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    df.to_excel(filename, index=False)
    masuk = df[df["Tipe"]=="MASUK"]["Jumlah"].sum()
    keluar = df[df["Tipe"]=="KELUAR"]["Jumlah"].sum()
    await update.message.reply_document(
        document=open(filename, 'rb'),
        filename=f"Laporan_Kas_V86_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        caption=f"📊 Export Excel V86 - 17 Anggota\nMasuk: {format_rp(masuk)}\nKeluar: {format_rp(keluar)}\nSaldo: {format_rp(masuk-keluar)}",
        parse_mode="Markdown"
    )
    os.remove(filename)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tambah", tambah))
    app.add_handler(CommandHandler("anggota", anggota_cmd))
    app.add_handler(CommandHandler("web", web_cmd))
    app.add_handler(CommandHandler("list", list_transaksi))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("hapus", hapus))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("laporan", laporan))
    app.add_handler(CommandHandler("excel", export_excel))
    app.add_handler(CommandHandler("export", export_excel))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot Kas EF V86 jalan... ALL 1,2,3 - Telegram -> Sheet -> Web")
    print(f"17 Anggota: {ANGGOTA_LIST}")
    print(f"Sheet: {GOOGLE_SHEET_ID}")
    print(f"Web: https://budidarwin00.github.io/Areaef-aski1/")
    app.run_polling()

if __name__ == "__main__":
    main()
