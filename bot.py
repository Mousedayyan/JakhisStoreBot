import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_USERNAME = "@jakhis27"

total_revenue = 0
item_terjual = 0
transaksi_sukses = 0
pending = 0
expired = 0
dibatalkan = 0
user_baru = set()


def admin_keyboard():
    keyboard = [
        ["📦 Produk", "🧩 Varian & Harga"],
        ["📦 Stok/Inventory", "🖼 Banner Global"],
        ["📜 SNK", "🧾 Transaksi"],
        ["📊 Laporan", "📣 Broadcast"],
        ["💰 Wallet Tools", "⚙️ Settings"],
        ["⏳ Perpanjang Sewa", "🧰 Tools"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def user_keyboard():
    keyboard = [
        ["📦 List Produk", "💰 Harga"],
        ["🛒 Cara Order", "👤 Hubungi Admin"],
        ["❓ FAQ", "✅ Garansi"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_baru.add(user_id)

    if user_id == ADMIN_ID:
        await update.message.reply_text(
            "👑 Admin Panel JakhisStore\n\nSilakan pilih menu:",
            reply_markup=admin_keyboard()
        )
    else:
        await update.message.reply_text(
            "Halo! Selamat datang di JakhisStore 👋\n\n"
            "Kami menyediakan app premium seperti Netflix, Spotify, YouTube Premium, Canva, dan lainnya.\n\n"
            "Silakan pilih menu:",
            reply_markup=user_keyboard()
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_revenue, item_terjual, transaksi_sukses, pending, expired, dibatalkan

    text = update.message.text
    user = update.message.from_user
    user_baru.add(user.id)

    # ADMIN MENU
    if user.id == ADMIN_ID:
        if text == "📊 Laporan":
            laporan = (
                "📊 LAPORAN: Bulan Ini\n\n"
                "┌────────────────────\n"
                f"💰 Total Revenue: Rp {total_revenue:,}\n"
                f"📦 Item Terjual: {item_terjual} pcs\n"
                f"✅ Transaksi Sukses: {transaksi_sukses}\n"
                f"⏳ Pending: {pending}\n"
                f"⌛ Expired: {expired}\n"
                f"❌ Dibatalkan: {dibatalkan}\n"
                f"👥 User Baru: {len(user_baru)}\n"
                "└────────────────────"
            )
            await update.message.reply_text(laporan, reply_markup=admin_keyboard())

        elif text == "📦 Produk":
            await update.message.reply_text(
                "📦 PRODUK\n\n"
                "1. Netflix Premium\n"
                "2. Spotify Premium\n"
                "3. YouTube Premium\n"
                "4. Canva Pro\n"
                "5. CapCut Pro",
                reply_markup=admin_keyboard()
            )

        elif text == "🧩 Varian & Harga":
            await update.message.reply_text(
                "🧩 VARIAN & HARGA\n\n"
                "Netflix: Rp25.000 / bulan\n"
                "Spotify: Rp15.000 / bulan\n"
                "YouTube Premium: Rp10.000 / bulan\n"
                "Canva Pro: Rp10.000 / bulan\n"
                "CapCut Pro: Rp15.000 / bulan",
                reply_markup=admin_keyboard()
            )

        elif text == "📦 Stok/Inventory":
            await update.message.reply_text(
                "📦 STOK / INVENTORY\n\n"
                "Netflix: Tersedia\n"
                "Spotify: Tersedia\n"
                "YouTube Premium: Tersedia\n"
                "Canva Pro: Tersedia\n"
                "CapCut Pro: Tersedia",
                reply_markup=admin_keyboard()
            )

        elif text == "🧾 Transaksi":
            await update.message.reply_text(
                "🧾 TRANSAKSI\n\nBelum ada database transaksi.\nNanti bisa kita upgrade otomatis.",
                reply_markup=admin_keyboard()
            )

        elif text == "📣 Broadcast":
            await update.message.reply_text(
                "📣 BROADCAST\n\nFitur broadcast belum aktif.\nNanti bisa kita tambah supaya admin bisa kirim pesan ke semua user.",
                reply_markup=admin_keyboard()
            )

        elif text == "⚙️ Settings":
            await update.message.reply_text(
                "⚙️ SETTINGS\n\nAdmin: aktif\nMode: online\nHosting: Railway",
                reply_markup=admin_keyboard()
            )

        else:
            await update.message.reply_text(
                "Menu admin belum aktif / pilih tombol yang tersedia.",
                reply_markup=admin_keyboard()
            )

        return

    # USER MENU
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
            "💰 DAFTAR HARGA\n\n"
            "Netflix: 25k / bulan\n"
            "Spotify: 15k / bulan\n"
            "YouTube: 10k / bulan\n"
            "Canva: 10k / bulan\n"
            "CapCut: 15k / bulan"
        )

    elif text == "🛒 Cara Order":
        await update.message.reply_text(
            "Ketik format ini:\n\n"
            "ORDER\n"
            "Nama:\n"
            "Produk:\n"
            "Durasi:"
        )

    elif text == "👤 Hubungi Admin":
        await update.message.reply_text(f"Hubungi admin: https://t.me/{ADMIN_USERNAME.replace('@', '')}")

    elif text == "❓ FAQ":
        await update.message.reply_text(
            "❓ FAQ\n\nAkun aktif setelah pembayaran dikonfirmasi.\nJika ada kendala, hubungi admin."
        )

    elif text == "✅ Garansi":
        await update.message.reply_text("✅ Garansi berlaku selama masa aktif jika akun bermasalah.")

    elif "order" in text.lower():
        pending += 1

        username = user.username if user.username else "Tidak ada username"

        pesan_admin = (
            "🔥 ORDER MASUK 🔥\n\n"
            f"Nama Telegram: {user.first_name}\n"
            f"Username: @{username}\n\n"
            f"Isi order:\n{text}"
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=pesan_admin)

        await update.message.reply_text(
            "✅ Order kamu sudah dikirim ke admin!\nTunggu konfirmasi ya."
        )

    else:
        await update.message.reply_text("Pilih menu yang tersedia ya.")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot JakhisStore admin panel sedang berjalan...")
app.run_polling()
