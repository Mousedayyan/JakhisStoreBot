import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
DB_NAME = "jakhisstore.db"


def db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            stock TEXT DEFAULT 'Tersedia'
        )
    """)
    conn.commit()
    conn.close()


def add_product(name, price):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        (name, price, "Tersedia")
    )
    conn.commit()
    conn.close()


def get_products():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_product(product_id):
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def update_stock(product_id, stock):
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE products SET stock = ? WHERE id = ?", (stock, product_id))
    conn.commit()
    conn.close()


def update_price(product_id, price):
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE products SET price = ? WHERE id = ?", (price, product_id))
    conn.commit()
    conn.close()


def admin_menu():
    keyboard = [
        ["➕ Tambah Produk", "📋 List Produk"],
        ["✏️ Edit Harga", "🔄 Edit Stok"],
        ["🗑 Hapus Produk"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id == ADMIN_ID:
        await update.message.reply_text(
            "👑 Admin Panel JakhisStore\n\nSilakan pilih menu:",
            reply_markup=admin_menu()
        )
    else:
        await update.message.reply_text(
            "Selamat datang di JakhisStore 👋\n\nSilakan hubungi admin untuk order."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("Bot ini khusus admin.")
        return

    mode = context.user_data.get("mode")

    if mode == "add_name":
        context.user_data["product_name"] = text
        context.user_data["mode"] = "add_price"
        await update.message.reply_text("Masukkan harga produk angka saja.\nContoh: 25000")
        return

    if mode == "add_price":
        try:
            price = int(text.replace(".", "").replace(",", ""))
        except ValueError:
            await update.message.reply_text("Harga harus angka.\nContoh: 25000")
            return

        name = context.user_data["product_name"]
        add_product(name, price)
        context.user_data.clear()

        await update.message.reply_text(
            f"✅ Produk berhasil ditambahkan!\n\nProduk: {name}\nHarga: Rp{price:,}\nStok: Tersedia",
            reply_markup=admin_menu()
        )
        return

    if mode == "edit_price_id":
        try:
            product_id = int(text)
        except ValueError:
            await update.message.reply_text("ID produk harus angka.")
            return

        context.user_data["edit_price_id"] = product_id
        context.user_data["mode"] = "edit_price_value"
        await update.message.reply_text("Masukkan harga baru.\nContoh: 30000")
        return

    if mode == "edit_price_value":
        try:
            price = int(text.replace(".", "").replace(",", ""))
        except ValueError:
            await update.message.reply_text("Harga harus angka.")
            return

        product_id = context.user_data["edit_price_id"]
        update_price(product_id, price)
        context.user_data.clear()

        await update.message.reply_text(
            f"✅ Harga produk #{product_id} diubah jadi Rp{price:,}",
            reply_markup=admin_menu()
        )
        return

    if mode == "edit_stock_id":
        try:
            product_id = int(text)
        except ValueError:
            await update.message.reply_text("ID produk harus angka.")
            return

        context.user_data["edit_stock_id"] = product_id
        context.user_data["mode"] = "edit_stock_value"
        await update.message.reply_text("Ketik stok baru: Tersedia / Kosong")
        return

    if mode == "edit_stock_value":
        product_id = context.user_data["edit_stock_id"]
        stock = text
        update_stock(product_id, stock)
        context.user_data.clear()

        await update.message.reply_text(
            f"✅ Stok produk #{product_id} diubah jadi {stock}",
            reply_markup=admin_menu()
        )
        return

    if mode == "delete_id":
        try:
            product_id = int(text)
        except ValueError:
            await update.message.reply_text("ID produk harus angka.")
            return

        delete_product(product_id)
        context.user_data.clear()

        await update.message.reply_text(
            f"🗑 Produk #{product_id} berhasil dihapus.",
            reply_markup=admin_menu()
        )
        return

    if text == "➕ Tambah Produk":
        context.user_data["mode"] = "add_name"
        await update.message.reply_text("Masukkan nama produk.\nContoh: Netflix Premium 1 Bulan")

    elif text == "📋 List Produk":
        products = get_products()

        if not products:
            await update.message.reply_text("Produk masih kosong.", reply_markup=admin_menu())
            return

        for product_id, name, price, stock in products:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Tersedia", callback_data=f"stock_{product_id}_Tersedia"),
                    InlineKeyboardButton("❌ Kosong", callback_data=f"stock_{product_id}_Kosong")
                ],
                [
                    InlineKeyboardButton("🗑 Hapus", callback_data=f"delete_{product_id}")
                ]
            ]

            await update.message.reply_text(
                f"#{product_id}\nProduk: {name}\nHarga: Rp{price:,}\nStok: {stock}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif text == "✏️ Edit Harga":
        context.user_data["mode"] = "edit_price_id"
        await update.message.reply_text("Masukkan ID produk yang mau diedit harganya.")

    elif text == "🔄 Edit Stok":
        context.user_data["mode"] = "edit_stock_id"
        await update.message.reply_text("Masukkan ID produk yang mau diedit stoknya.")

    elif text == "🗑 Hapus Produk":
        context.user_data["mode"] = "delete_id"
        await update.message.reply_text("Masukkan ID produk yang mau dihapus.")

    else:
        await update.message.reply_text("Pilih menu yang tersedia.", reply_markup=admin_menu())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("Kamu bukan admin.")
        return

    data = query.data

    if data.startswith("delete_"):
        product_id = int(data.split("_")[1])
        delete_product(product_id)
        await query.edit_message_text(f"🗑 Produk #{product_id} berhasil dihapus.")

    elif data.startswith("stock_"):
        _, product_id, stock = data.split("_")
        product_id = int(product_id)
        update_stock(product_id, stock)
        await query.edit_message_text(f"✅ Stok produk #{product_id} diubah jadi: {stock}")


if __name__ == "__main__":
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot JakhisStore final running...")
    app.run_polling()
