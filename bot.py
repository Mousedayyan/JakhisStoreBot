import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

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
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        stock TEXT DEFAULT 'Tersedia'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        first_name TEXT,
        username TEXT,
        order_text TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_user(user):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, first_name, username) VALUES (?, ?, ?)",
        (user.id, user.first_name or "", user.username or "")
    )
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


def save_order(user, text):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, first_name, username, order_text) VALUES (?, ?, ?, ?)",
        (user.id, user.first_name or "", user.username or "", text)
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id


def laporan_data():
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status='pending'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status='success'")
    success = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status='cancel'")
    cancel = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM products")
    products = cur.fetchone()[0]

    conn.close()
    return users, orders, pending, success, cancel, products


def admin_menu():
    keyboard = [
        ["📦 Produk", "🧩 Varian & Harga"],
        ["📦 Stok/Inventory", "🖼 Banner Global"],
        ["📜 SNK", "🧾 Transaksi"],
        ["📊 Laporan", "📣 Broadcast"],
        ["💰 Wallet Tools", "⚙️ Settings"],
        ["⏳ Perpanjang Sewa", "🧰 Tools"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def product_action_menu():
    keyboard = [
        ["➕ Tambah Produk", "📋 List Produk"],
        ["✏️ Edit Harga", "🔄 Edit Stok"],
        ["🗑 Hapus Produk", "⬅️ Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def user_menu():
    keyboard = [
        ["📦 List Produk", "💰 Harga"],
        ["🛒 Cara Order", "👤 Hubungi Admin"],
        ["❓ FAQ", "✅ Garansi"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def format_products(show_price=True):
    products = get_products()

    if not products:
        return "📦 Belum ada produk.\n\nAdmin bisa tambah produk lewat menu 📦 Produk → ➕ Tambah Produk."

    msg = "📦 LIST PRODUK\n\n"
    for product_id, name, price, stock in products:
        if show_price:
            msg += f"#{product_id} - {name}\nHarga: Rp{price:,}\nStok: {stock}\n\n"
        else:
            msg += f"#{product_id} - {name}\nStok: {stock}\n\n"
    return msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    save_user(user)
    context.user_data.clear()

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👑 Admin Panel JakhisStore\n\nSilakan pilih menu:",
            reply_markup=admin_menu()
        )
    else:
        await update.message.reply_text(
            "Selamat datang di JakhisStore 👋\n\nSilakan pilih menu:",
            reply_markup=user_menu()
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    save_user(user)

    if user.id == ADMIN_ID:
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
                reply_markup=product_action_menu()
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
                reply_markup=product_action_menu()
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
                reply_markup=product_action_menu()
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
                reply_markup=product_action_menu()
            )
            return

        if text == "📦 Produk":
            await update.message.reply_text(
                "📦 MENU PRODUK\n\nPilih aksi produk:",
                reply_markup=product_action_menu()
            )

        elif text == "➕ Tambah Produk":
            context.user_data["mode"] = "add_name"
            await update.message.reply_text("Masukkan nama produk.\nContoh: Netflix Premium 1 Bulan")

        elif text == "📋 List Produk":
            products = get_products()
            if not products:
                await update.message.reply_text("Produk masih kosong.", reply_markup=product_action_menu())
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

        elif text == "⬅️ Back":
            context.user_data.clear()
            await update.message.reply_text("Kembali ke admin panel.", reply_markup=admin_menu())

        elif text == "🧩 Varian & Harga":
            await update.message.reply_text(format_products(show_price=True), reply_markup=admin_menu())

        elif text == "📦 Stok/Inventory":
            await update.message.reply_text(format_products(show_price=False), reply_markup=admin_menu())

        elif text == "🖼 Banner Global":
            await update.message.reply_text("🖼 Banner Global belum aktif.", reply_markup=admin_menu())

        elif text == "📜 SNK":
            await update.message.reply_text(
                "📜 SNK\n\n"
                "1. Produk diproses setelah pembayaran.\n"
                "2. Garansi berlaku selama masa aktif.\n"
                "3. Refund mengikuti kebijakan admin.",
                reply_markup=admin_menu()
            )

        elif text == "🧾 Transaksi":
            conn = db()
            cur = conn.cursor()
            cur.execute("SELECT id, first_name, username, status FROM orders ORDER BY id DESC LIMIT 10")
            rows = cur.fetchall()
            conn.close()

            if not rows:
                await update.message.reply_text("🧾 Belum ada transaksi.", reply_markup=admin_menu())
            else:
                msg = "🧾 TRANSAKSI TERBARU\n\n"
                for row in rows:
                    msg += f"#{row[0]} | {row[1]} | @{row[2]} | {row[3]}\n"
                await update.message.reply_text(msg, reply_markup=admin_menu())

        elif text == "📊 Laporan":
            users, orders, pending, success, cancel, products = laporan_data()
            await update.message.reply_text(
                "📊 LAPORAN: Bulan Ini\n\n"
                "┌────────────────────\n"
                f"💰 Total Revenue: Rp 0\n"
                f"📦 Total Produk: {products}\n"
                f"🧾 Total Order: {orders}\n"
                f"✅ Transaksi Sukses: {success}\n"
                f"⏳ Pending: {pending}\n"
                "⌛ Expired: 0\n"
                f"❌ Dibatalkan: {cancel}\n"
                f"👥 User Baru: {users}\n"
                "└────────────────────",
                reply_markup=admin_menu()
            )

        elif text == "📣 Broadcast":
            await update.message.reply_text("📣 Broadcast belum aktif.", reply_markup=admin_menu())

        elif text == "💰 Wallet Tools":
            await update.message.reply_text("💰 Wallet Tools belum aktif.\nNanti bisa isi DANA/OVO/Gopay/QRIS.", reply_markup=admin_menu())

        elif text == "⚙️ Settings":
            await update.message.reply_text(
                "⚙️ SETTINGS\n\n"
                "Database: SQLite aktif\n"
                "Produk DB: aktif\n"
                "Hosting: Railway\n"
                f"Admin: @{ADMIN_USERNAME}",
                reply_markup=admin_menu()
            )

        elif text == "⏳ Perpanjang Sewa":
            await update.message.reply_text("⏳ Perpanjang Sewa belum aktif.", reply_markup=admin_menu())

        elif text == "🧰 Tools":
            await update.message.reply_text("🧰 Tools belum aktif.", reply_markup=admin_menu())

        else:
            await update.message.reply_text("Menu admin belum aktif / pilih tombol yang tersedia.", reply_markup=admin_menu())

        return

    if text == "📦 List Produk":
        await update.message.reply_text(format_products(show_price=False), reply_markup=user_menu())

    elif text == "💰 Harga":
        await update.message.reply_text(format_products(show_price=True), reply_markup=user_menu())

    elif text == "🛒 Cara Order":
        await update.message.reply_text(
            "🛒 CARA ORDER\n\n"
            "Ketik format ini:\n\n"
            "ORDER\n"
            "Nama:\n"
            "Produk:\n"
            "Durasi:",
            reply_markup=user_menu()
        )

    elif text == "👤 Hubungi Admin":
        await update.message.reply_text(
            f"Hubungi admin: https://t.me/{ADMIN_USERNAME}",
            reply_markup=user_menu()
        )

    elif text == "❓ FAQ":
        await update.message.reply_text(
            "❓ FAQ\n\nAkun aktif setelah pembayaran dikonfirmasi.\nJika ada kendala, hubungi admin.",
            reply_markup=user_menu()
        )

    elif text == "✅ Garansi":
        await update.message.reply_text("✅ Garansi berlaku selama masa aktif.", reply_markup=user_menu())

    elif "order" in text.lower():
        order_id = save_order(user, text)
        username = user.username if user.username else "tidak_ada"

        pesan_admin = (
            "🔥 ORDER MASUK 🔥\n\n"
            f"ID Order: #{order_id}\n"
            f"Nama Telegram: {user.first_name}\n"
            f"Username: @{username}\n\n"
            f"Isi Order:\n{text}"
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=pesan_admin)

        await update.message.reply_text(
            f"✅ Order diterima!\nID Order kamu: #{order_id}\nAdmin akan segera menghubungi kamu.",
            reply_markup=user_menu()
        )

    else:
        await update.message.reply_text("❗ Pilih menu yang tersedia.", reply_markup=user_menu())


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

    print("Bot JakhisStore panel besar running...")
    app.run_polling()
