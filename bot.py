import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_USERNAME = "jakhis27"
DB_NAME = "jakhisstore.db"


def db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        stock TEXT DEFAULT 'Tersedia'
    )
    """)

    conn.commit()
    conn.close()


def add_product(name, price):
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()


def get_products():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products")
    data = cur.fetchall()
    conn.close()
    return data


def delete_product(pid):
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()


def update_price(pid, price):
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE products SET price=? WHERE id=?", (price, pid))
    conn.commit()
    conn.close()


def update_stock(pid, stock):
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE products SET stock=? WHERE id=?", (stock, pid))
    conn.commit()
    conn.close()


def admin_menu():
    keyboard = [
        ["➕ Tambah Produk", "📋 List Produk"],
        ["🗑 Hapus Produk", "✏️ Edit Harga"],
        ["🔄 Edit Stok"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 Admin Panel", reply_markup=admin_menu())
    else:
        await update.message.reply_text("User menu aktif")


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        return

    # TAMBAH PRODUK
    if text == "➕ Tambah Produk":
        context.user_data["mode"] = "nama"
        await update.message.reply_text("Masukkan nama produk")

    elif context.user_data.get("mode") == "nama":
        context.user_data["nama"] = text
        context.user_data["mode"] = "harga"
        await update.message.reply_text("Masukkan harga")

    elif context.user_data.get("mode") == "harga":
        harga = int(text)
        add_product(context.user_data["nama"], harga)
        context.user_data.clear()
        await update.message.reply_text("Produk ditambahkan ✅")

    # LIST PRODUK
    elif text == "📋 List Produk":
        data = get_products()
        msg = ""
        for p in data:
            msg += f"{p[0]}. {p[1]} - Rp{p[2]} ({p[3]})\n"
        await update.message.reply_text(msg or "Kosong")

    # HAPUS PRODUK
    elif text.startswith("HAPUS"):
        try:
            pid = int(text.split()[1])
            delete_product(pid)
            await update.message.reply_text("Produk dihapus ✅")
        except:
            await update.message.reply_text("Format: HAPUS ID")

    # EDIT HARGA
    elif text.startswith("HARGA"):
        try:
            _, pid, harga = text.split()
            update_price(int(pid), int(harga))
            await update.message.reply_text("Harga diupdate ✅")
        except:
            await update.message.reply_text("Format: HARGA ID HARGA")

    # EDIT STOK
    elif text.startswith("STOK"):
        try:
            _, pid, *stok = text.split()
            update_stock(int(pid), " ".join(stok))
            await update.message.reply_text("Stok diupdate ✅")
        except:
            await update.message.reply_text("Format: STOK ID STATUS")

    else:
        await update.message.reply_text("Gunakan menu / format yang benar")


if __name__ == "__main__":
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))

    print("Bot running...")
    app.run_polling()
