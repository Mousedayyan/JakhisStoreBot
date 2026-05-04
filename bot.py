import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_USERNAME = "jakhis27"  # tanpa @

users = set()
orders = []
total_revenue = 0


def user_menu():
    keyboard = [
        ["📦 List Produk", "💰 Harga"],
        ["🛒 Cara Order", "👤 Hubungi Admin"],
        ["❓ FAQ", "✅ Garansi"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def admin_menu():
    keyboard = [
        ["📦 Produk", "🧩 Varian & Harga"],
        ["📦 Stok/Inventory", "🖼 Banner Global"],
        ["📜 SNK", "🧾 Transaksi"],
        ["📊 Laporan", "📣 Broadcast"],
        ["💰 Wallet Tools", "⚙️ Settings"],
        ["⏳ Perpanjang Sewa", "🧰 Tools"],
        ["👥 Mode User"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    users.add(user.id)

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
    global total_revenue

    text = update.message.text
    user = update.message.from_user
    users.add(user.id)

    # ADMIN PANEL
    if user.id == ADMIN_ID:
        if text == "📊 Laporan":
            await update.message.reply_text(
                "📊 LAPORAN: Bulan Ini\n\n"
                "┌────────────────────\n"
                f"💰 Total Revenue: Rp {total_revenue:,}\n"
                f"📦 Item Terjual: {len(orders)} pcs\n"
                f"✅ Transaksi Sukses: {len(orders)}\n"
                "⏳ Pending: 0\n"
                "⌛ Expired: 0\n"
                "❌ Dibatalkan: 0\n"
                f"👥 User Baru: {len(users)}\n"
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
            if not orders:
                await update.message.reply_text(
                    "🧾 TRANSAKSI\n\nBelum ada transaksi.",
                    reply_markup=admin_menu()
                )
            else:
                await update.message.reply_text(
                    "🧾 TRANSAKSI TERBARU\n\n" + "\n\n".join(orders[-5:]),
                    reply_markup=admin_menu()
                )

        elif text == "📣 Broadcast":
            await update.message.reply_text(
                "📣 BROADCAST\n\nFitur broadcast belum aktif.",
                reply_markup=admin_menu()
            )

        elif text == "⚙️ Settings":
            await update.message.reply_text(
                "⚙️ SETTINGS\n\n"
                "Status: Online\n"
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
                "Pilih menu admin yang tersedia.",
                reply_markup=admin_menu()
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
        order_text = (
            f"Nama Telegram: {user.first_name}\n"
            f"Username: @{user.username if user.username else 'tidak_ada'}\n"
            f"Isi Order:\n{text}"
        )
        orders.append(order_text)

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="🔥 ORDER MASUK 🔥\n\n" + order_text
        )

        await update.message.reply_text(
            "✅ Order diterima!\nAdmin akan segera menghubungi kamu."
        )

    else:
        await update.message.reply_text("❗ Pilih menu yang tersedia.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot JakhisStore admin panel running...")
    app.run_polling()
