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
        (user.id, user.first_name, user.username or "")
    )
    conn.commit()
    conn.close()


def save_order(user, text):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, first_name, username, order_text) VALUES (?, ?, ?, ?)",
        (user.id, user.first_name, user.username or "", text)
    )
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id


def laporan_data():
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders")
    total_orders = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status='pending'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status='success'")
    success = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM orders WHERE status='cancel'")
    cancel = cur.fetchone()[0]

    conn.close()

    return total_users, total_orders, pending, success, cancel


def admin_menu():
    keyboard = [
        ["📦 Produk", "🧩 Varian & Harga"],
        ["📦 Stok/Inventory", "🧾 Transaksi"],
        ["📊 Laporan", "📣 Broadcast"],
        ["💰 Wallet Tools", "⚙️ Settings"],
        ["👥 Mode User"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def user_menu():
    keyboard = [
        ["📦 List Produk", "💰 Harga"],
        ["🛒 Cara Order", "👤 Hubungi Admin"],
        ["❓ FAQ", "✅ Garansi"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    save_user(user)

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
        if text == "📊 Laporan":
            total_users, total_orders, pending, success, cancel = laporan_data()

            await update.message.reply_text(
                "📊 LAPORAN DATABASE\n\n"
                "┌────────────────────\n"
                f"👥 Total User: {total_users}\n"
                f"📦 Total Order: {total_orders}\n"
                f"⏳ Pending: {pending}\n"
                f"✅ Sukses: {success}\n"
                f"❌ Batal: {cancel}\n"
                "└────────────────────",
                reply_markup=admin_menu()
            )

        elif text == "📦 Produk":
            await update.message.reply_text(
                "📦 PRODUK\n\n"
                "1. Netflix Premium\n"
                "2. Spotify Premium\n"
                "3. YouTube Premium\n"
                "4. Canva Pro\n"
                "5. CapCut Pro",
                reply_markup=admin_menu()
            )

        elif text == "🧩 Varian & Harga":
            await update.message.reply_text(
                "🧩 VARIAN & HARGA\n\n"
                "Netflix: Rp25.000 / bulan\n"
                "Spotify: Rp20.000 / bulan\n"
                "YouTube: Rp15.000 / bulan\n"
                "Canva: Rp10.000 / bulan\n"
                "CapCut: Rp10.000 / bulan",
                reply_markup=admin_menu()
            )

        elif text == "📦 Stok/Inventory":
            await update.message.reply_text(
                "📦 STOK / INVENTORY\n\n"
                "Netflix: Tersedia\n"
                "Spotify: Tersedia\n"
                "YouTube: Tersedia\n"
                "Canva: Tersedia\n"
                "CapCut: Tersedia",
                reply_markup=admin_menu()
            )

        elif text == "🧾 Transaksi":
            conn = db()
            cur = conn.cursor()
            cur.execute("SELECT id, first_name, username, status FROM orders ORDER BY id DESC LIMIT 5")
            rows = cur.fetchall()
            conn.close()

            if not rows:
                await update.message.reply_text("🧾 Belum ada transaksi.", reply_markup=admin_menu())
            else:
                msg = "🧾 TRANSAKSI TERBARU\n\n"
                for r in rows:
                    msg += f"#{r[0]} | {r[1]} | @{r[2]} | {r[3]}\n"

                await update.message.reply_text(msg, reply_markup=admin_menu())

        elif text == "📣 Broadcast":
            await update.message.reply_text(
                "📣 Broadcast belum aktif. Next step kita aktifkan.",
                reply_markup=admin_menu()
            )

        elif text == "⚙️ Settings":
            await update.message.reply_text(
                "⚙️ SETTINGS\n\n"
                "Database: SQLite aktif\n"
                "Hosting: Railway\n"
                f"Admin: @{ADMIN_USERNAME}",
                reply_markup=admin_menu()
            )

        elif text == "👥 Mode User":
            await update.message.reply_text(
                "Mode user aktif.",
                reply_markup=user_menu()
            )

        else:
            await update.message.reply_text(
                "Menu admin belum aktif / pilih tombol yang tersedia.",
                reply_markup=admin_menu()
            )

        return

    if text == "📦 List Produk":
        await update.message.reply_text(
            "📦 LIST PRODUK\n\n"
            "Netflix Premium\n"
            "Spotify Premium\n"
            "YouTube Premium\n"
            "Canva Pro\n"
            "CapCut Pro"
        )

    elif text == "💰 Harga":
        await update.message.reply_text(
            "💰 HARGA\n\n"
            "Netflix: 25k\n"
            "Spotify: 20k\n"
            "YouTube: 15k\n"
            "Canva: 10k\n"
            "CapCut: 10k"
        )

    elif text == "🛒 Cara Order":
        await update.message.reply_text(
            "🛒 CARA ORDER\n\n"
            "Ketik format ini:\n\n"
            "ORDER\n"
            "Nama:\n"
            "Produk:\n"
            "Durasi:"
        )

    elif text == "👤 Hubungi Admin":
        await update.message.reply_text(
            f"Hubungi admin: https://t.me/{ADMIN_USERNAME}"
        )

    elif text == "❓ FAQ":
        await update.message.reply_text(
            "❓ FAQ\n\n"
            "Akun aktif setelah pembayaran dikonfirmasi.\n"
            "Jika ada kendala, hubungi admin."
        )

    elif text == "✅ Garansi":
        await update.message.reply_text(
            "✅ Garansi berlaku selama masa aktif."
        )

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
            f"✅ Order diterima!\nID Order kamu: #{order_id}\nAdmin akan segera menghubungi kamu."
        )

    else:
        await update.message.reply_text("❗ Pilih menu yang tersedia.")


if __name__ == "__main__":
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot JakhisStore database running...")
    app.run_polling()
