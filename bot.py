import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

ADMIN_USERNAME = "jakhis27"
PAYMENT_NAME = "IKATJANJI"
QRIS_IMAGE_URL = "https://raw.githubusercontent.com/Mousedayyan/JakhisStoreBot/main/qris.jpg"

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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS digital_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        content TEXT,
        status TEXT DEFAULT 'available'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        first_name TEXT,
        username TEXT,
        product_id INTEGER,
        product_name TEXT,
        price INTEGER,
        status TEXT DEFAULT 'pending_payment',
        delivered_stock_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


def get_product(product_id):
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row


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


def add_digital_stock(product_id, content):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO digital_stock (product_id, content, status) VALUES (?, ?, 'available')",
        (product_id, content)
    )
    conn.commit()
    conn.close()


def get_stock_count(product_id):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM digital_stock WHERE product_id = ? AND status = 'available'",
        (product_id,)
    )
    count = cur.fetchone()[0]
    conn.close()
    return count


def take_available_stock(product_id):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, content FROM digital_stock WHERE product_id = ? AND status = 'available' ORDER BY id ASC LIMIT 1",
        (product_id,)
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return None

    stock_id, content = row

    cur.execute("UPDATE digital_stock SET status = 'used' WHERE id = ?", (stock_id,))
    conn.commit()
    conn.close()

    return stock_id, content


def create_order(user, product_id, product_name, price):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO orders (user_id, first_name, username, product_id, product_name, price, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending_payment')
        """,
        (
            user.id,
            user.first_name or "",
            user.username or "",
            product_id,
            product_name,
            price
        )
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id


def get_order(order_id):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, user_id, first_name, username, product_id, product_name, price, status
        FROM orders WHERE id = ?
        """,
        (order_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def update_order_paid(order_id, delivered_stock_id=None):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE orders SET status = 'paid', delivered_stock_id = ? WHERE id = ?",
        (delivered_stock_id, order_id)
    )
    conn.commit()
    conn.close()


def update_order_status(order_id, status):
    conn = db()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def get_latest_orders(limit=10):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, first_name, username, product_name, price, status
        FROM orders
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def laporan_data():
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM products")
    total_products = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending_payment'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'paid'")
    paid = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'cancelled'")
    cancelled = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(price), 0) FROM orders WHERE status = 'paid'")
    revenue = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM digital_stock WHERE status = 'available'")
    available_stock = cur.fetchone()[0]

    conn.close()
    return total_products, total_orders, pending, paid, cancelled, revenue, available_stock


def admin_menu():
    keyboard = [
        ["📦 Produk", "📊 Laporan"],
        ["🧾 Transaksi", "⚙️ Settings"],
        ["👥 Mode User"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def product_menu():
    keyboard = [
        ["➕ Tambah Produk", "📋 List Produk"],
        ["📥 Tambah Stok Digital", "⬅️ Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def user_menu():
    keyboard = [
        ["🛒 Order Produk", "📦 List Produk"],
        ["💰 Harga", "👤 Hubungi Admin"],
        ["🔙 Mode Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data.clear()

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👑 Admin Panel IKATJANJI\n\nSilakan pilih menu:",
            reply_markup=admin_menu()
        )
    else:
        await update.message.reply_text(
            "Selamat datang di IKATJANJI 👋\n\nSilakan pilih menu:",
            reply_markup=user_menu()
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    admin_as_user = user.id == ADMIN_ID and context.user_data.get("view_mode") == "user"
    is_admin_mode = user.id == ADMIN_ID and not admin_as_user

    if is_admin_mode:
        mode = context.user_data.get("mode")

        if mode == "add_product_name":
            context.user_data["product_name"] = text
            context.user_data["mode"] = "add_product_price"
            await update.message.reply_text("Masukkan harga produk angka saja.\nContoh: 25000")
            return

        if mode == "add_product_price":
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
                reply_markup=product_menu()
            )
            return

        if mode == "add_stock_product_id":
            try:
                product_id = int(text)
            except ValueError:
                await update.message.reply_text("ID produk harus angka.")
                return

            product = get_product(product_id)
            if not product:
                await update.message.reply_text("Produk tidak ditemukan.")
                return

            context.user_data["stock_product_id"] = product_id
            context.user_data["mode"] = "add_stock_content"
            await update.message.reply_text(
                "Kirim stok digitalnya.\n\n"
                "Contoh:\n"
                "Email: contoh@gmail.com\n"
                "Password: 123456\n"
                "Catatan: berlaku 1 bulan"
            )
            return

        if mode == "add_stock_content":
            product_id = context.user_data["stock_product_id"]
            add_digital_stock(product_id, text)
            context.user_data.clear()

            count = get_stock_count(product_id)
            await update.message.reply_text(
                f"✅ Stok digital berhasil ditambahkan.\nSisa stok produk #{product_id}: {count}",
                reply_markup=product_menu()
            )
            return

        if text == "📦 Produk":
            await update.message.reply_text(
                "📦 Menu Produk\n\nPilih aksi:",
                reply_markup=product_menu()
            )

        elif text == "➕ Tambah Produk":
            context.user_data["mode"] = "add_product_name"
            await update.message.reply_text("Masukkan nama produk.\nContoh: Netflix Premium 1 Bulan")

        elif text == "📥 Tambah Stok Digital":
            context.user_data["mode"] = "add_stock_product_id"
            await update.message.reply_text(
                "Masukkan ID produk yang mau ditambahkan stok digital.\n\n"
                "Cek ID lewat 📋 List Produk."
            )

        elif text == "📋 List Produk":
            products = get_products()

            if not products:
                await update.message.reply_text("Produk masih kosong.", reply_markup=product_menu())
                return

            for product_id, name, price, stock in products:
                stock_count = get_stock_count(product_id)
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
                    f"#{product_id}\n"
                    f"Produk: {name}\n"
                    f"Harga: Rp{price:,}\n"
                    f"Status: {stock}\n"
                    f"Stok digital tersedia: {stock_count}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

        elif text == "⬅️ Back":
            context.user_data.clear()
            await update.message.reply_text("Kembali ke admin panel.", reply_markup=admin_menu())

        elif text == "🧾 Transaksi":
            rows = get_latest_orders()

            if not rows:
                await update.message.reply_text("🧾 Belum ada transaksi.", reply_markup=admin_menu())
                return

            for order_id, first_name, username, product_name, price, status in rows:
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Tandai Paid + Kirim", callback_data=f"paid_{order_id}"),
                        InlineKeyboardButton("❌ Batalkan", callback_data=f"cancel_{order_id}")
                    ]
                ]

                await update.message.reply_text(
                    f"🧾 Order #{order_id}\n"
                    f"User: {first_name} (@{username or 'tidak_ada'})\n"
                    f"Produk: {product_name}\n"
                    f"Harga: Rp{price:,}\n"
                    f"Status: {status}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

        elif text == "📊 Laporan":
            total_products, total_orders, pending, paid, cancelled, revenue, available_stock = laporan_data()

            await update.message.reply_text(
                "📊 LAPORAN\n\n"
                f"💰 Total Revenue: Rp{revenue:,}\n"
                f"📦 Total Produk: {total_products}\n"
                f"📥 Stok Digital Ready: {available_stock}\n"
                f"🧾 Total Order: {total_orders}\n"
                f"⏳ Pending Payment: {pending}\n"
                f"✅ Paid: {paid}\n"
                f"❌ Cancelled: {cancelled}",
                reply_markup=admin_menu()
            )

        elif text == "⚙️ Settings":
            await update.message.reply_text(
                "⚙️ SETTINGS\n\n"
                f"Admin: @{ADMIN_USERNAME}\n"
                f"Payment: QRIS\n"
                f"Nama Payment: {PAYMENT_NAME}",
                reply_markup=admin_menu()
            )

        elif text == "👥 Mode User":
            context.user_data.clear()
            context.user_data["view_mode"] = "user"
            await update.message.reply_text(
                "👥 Mode User aktif.\n\nKetik /start untuk kembali ke Admin Panel.",
                reply_markup=user_menu()
            )

        else:
            await update.message.reply_text("Pilih menu admin.", reply_markup=admin_menu())

        return

    # USER MODE
    if text == "🔙 Mode Admin" and user.id == ADMIN_ID:
        context.user_data.clear()
        await update.message.reply_text(
            "👑 Kembali ke Admin Panel.",
            reply_markup=admin_menu()
        )
        return

    if text == "🛒 Order Produk":
        products = get_products()

        if not products:
            await update.message.reply_text("Produk belum tersedia.", reply_markup=user_menu())
            return

        for product_id, name, price, stock in products:
            stock_count = get_stock_count(product_id)

            if stock.lower() == "kosong" or stock_count <= 0:
                button_text = "❌ Stok Kosong"
                callback = "noop"
            else:
                button_text = "🛒 Order Sekarang"
                callback = f"order_{product_id}"

            await update.message.reply_text(
                f"📦 {name}\n💰 Harga: Rp{price:,}\n📌 Stok: {stock}\n📥 Ready: {stock_count}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(button_text, callback_data=callback)]
                ])
            )

    elif text == "📦 List Produk":
        products = get_products()
        if not products:
            await update.message.reply_text("Produk belum tersedia.", reply_markup=user_menu())
            return

        msg = "📦 LIST PRODUK\n\n"
        for product_id, name, price, stock in products:
            stock_count = get_stock_count(product_id)
            msg += f"#{product_id} - {name}\nStok: {stock}\nReady: {stock_count}\n\n"

        await update.message.reply_text(msg, reply_markup=user_menu())

    elif text == "💰 Harga":
        products = get_products()
        if not products:
            await update.message.reply_text("Produk belum tersedia.", reply_markup=user_menu())
            return

        msg = "💰 DAFTAR HARGA\n\n"
        for product_id, name, price, stock in products:
            stock_count = get_stock_count(product_id)
            msg += f"{name}: Rp{price:,}\nStok: {stock}\nReady: {stock_count}\n\n"

        await update.message.reply_text(msg, reply_markup=user_menu())

    elif text == "👤 Hubungi Admin":
        await update.message.reply_text(
            f"Hubungi admin: https://t.me/{ADMIN_USERNAME}",
            reply_markup=user_menu()
        )

    else:
        await update.message.reply_text("Pilih menu yang tersedia.", reply_markup=user_menu())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user

    if data == "noop":
        await query.answer("Stok produk ini kosong.", show_alert=True)
        return

    if data.startswith("order_"):
        product_id = int(data.split("_")[1])
        product = get_product(product_id)

        if not product:
            await query.edit_message_text("Produk tidak ditemukan.")
            return

        _, name, price, stock = product
        stock_count = get_stock_count(product_id)

        if stock.lower() == "kosong" or stock_count <= 0:
            await query.edit_message_text("Maaf, stok produk ini kosong.")
            return

        order_id = create_order(user, product_id, name, price)
        username = user.username if user.username else "tidak_ada"

        await query.edit_message_text(
            f"✅ Order dibuat!\n\n"
            f"ID Order: #{order_id}\n"
            f"Produk: {name}\n"
            f"Harga: Rp{price:,}\n\n"
            f"Silakan scan QRIS untuk pembayaran.\n"
            f"Nama merchant: {PAYMENT_NAME}\n\n"
            f"Setelah bayar, kirim bukti pembayaran ke admin:\n"
            f"https://t.me/{ADMIN_USERNAME}"
        )

        if QRIS_IMAGE_URL:
            await context.bot.send_photo(
                chat_id=user.id,
                photo=QRIS_IMAGE_URL,
                caption=(
                    f"QRIS Pembayaran\n"
                    f"Order #{order_id}\n"
                    f"Total: Rp{price:,}"
                )
            )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔥 ORDER MASUK 🔥\n\n"
                f"ID Order: #{order_id}\n"
                f"User: {user.first_name} (@{username})\n"
                f"Produk: {name}\n"
                f"Harga: Rp{price:,}\n"
                f"Status: Menunggu pembayaran\n\n"
                "Masuk menu 🧾 Transaksi lalu klik ✅ Tandai Paid + Kirim."
            )
        )
        return

    if user.id != ADMIN_ID:
        await query.edit_message_text("Kamu bukan admin.")
        return

    if data.startswith("delete_"):
        product_id = int(data.split("_")[1])
        delete_product(product_id)
        await query.edit_message_text(f"🗑 Produk #{product_id} berhasil dihapus.")

    elif data.startswith("stock_"):
        _, product_id, stock = data.split("_")
        update_stock(int(product_id), stock)
        await query.edit_message_text(f"✅ Stok produk #{product_id} diubah jadi: {stock}")

    elif data.startswith("paid_"):
        order_id = int(data.split("_")[1])
        order = get_order(order_id)

        if not order:
            await query.edit_message_text("Order tidak ditemukan.")
            return

        _, user_id, first_name, username, product_id, product_name, price, status = order

        if status == "paid":
            await query.edit_message_text(f"Order #{order_id} sudah paid.")
            return

        stock_item = take_available_stock(product_id)

        if not stock_item:
            await query.edit_message_text(
                f"❌ Tidak ada stok digital tersedia untuk produk {product_name}.\n"
                "Tambahkan stok dulu lewat 📦 Produk → 📥 Tambah Stok Digital."
            )
            return

        stock_id, content = stock_item
        update_order_paid(order_id, delivered_stock_id=stock_id)

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ Pembayaran dikonfirmasi!\n\n"
                f"Order #{order_id}\n"
                f"Produk: {product_name}\n\n"
                f"Berikut data digital kamu:\n\n"
                f"{content}\n\n"
                "Terima kasih sudah order di IKATJANJI."
            )
        )

        await query.edit_message_text(
            f"✅ Order #{order_id} PAID dan stok digital sudah dikirim ke user."
        )

    elif data.startswith("cancel_"):
        order_id = int(data.split("_")[1])
        update_order_status(order_id, "cancelled")
        await query.edit_message_text(f"❌ Order #{order_id} dibatalkan.")


if __name__ == "__main__":
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot IKATJANJI auto delivery running...")
    app.run_polling()
