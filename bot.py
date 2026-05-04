from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERNAME = "@jakhis"
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # ganti dengan ID kamu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📦 List Produk", "💰 Harga"],
        ["🛒 Cara Order", "👤 Hubungi Admin"],
        ["❓ FAQ", "✅ Garansi"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Halo! Selamat datang di JakhisStore 👋\n\n"
        "Kami menyediakan berbagai app premium.\n\n"
        "Silakan pilih menu di bawah:",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📦 List Produk":
        await update.message.reply_text(
            "📦 LIST PRODUK\n\nNetflix\nSpotify\nYouTube\nCanva\nCapCut"
        )

    elif text == "💰 Harga":
        await update.message.reply_text(
            "💰 HARGA\n\nNetflix: 25k\nSpotify: 15k\nYouTube: 10k"
        )

    elif text == "🛒 Cara Order":
        await update.message.reply_text(
            "Ketik:\nORDER\nNama:\nProduk:\nDurasi:"
        )

    elif text == "👤 Hubungi Admin":
        await update.message.reply_text("Chat admin: @jakhis")

    elif "order" in text.lower():
        user = update.message.from_user

        pesan_admin = (
            "🔥 ORDER MASUK 🔥\n\n"
            f"Nama: {user.first_name}\n"
            f"Username: @{user.username}\n\n"
            f"Isi order:\n{text}"
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=pesan_admin)
i
        await update.message.reply_text(
            "✅ Order kamu sudah dikirim ke admin!"
        )

    else:
        await update.message.reply_text("Pilih menu ya.")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot JakhisStore sedang berjalan...")
app.run_polling()