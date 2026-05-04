import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_USERNAME = "@jakhis27"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📦 List Produk", "💰 Harga"],
        ["🛒 Cara Order", "👤 Hubungi Admin"],
        ["❓ FAQ", "✅ Garansi"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Halo! Selamat datang di JakhisStore 👋\n\n"
        "Silakan pilih menu:",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

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
        await update.message.reply_text(f"Chat admin: https://t.me/jakhis27")

    elif text == "❓ FAQ":
        await update.message.reply_text(
            "❓ FAQ\n\n"
            "Akun aktif setelah pembayaran dikonfirmasi.\n"
            "Jika ada kendala, hubungi admin."
        )

    elif text == "✅ Garansi":
        await update.message.reply_text(
            "✅ Garansi berlaku selama masa aktif jika akun bermasalah."
        )

    elif "order" in text.lower():
        user = update.message.from_user
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

print("Bot JakhisStore sedang berjalan...")
app.run_polling()
