import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Load environment variables
load_dotenv()

# Configuration
TOKEN = os.getenv("TELEGRAM_TOKEN")
PASSWORD = os.getenv("ADMIN_PASSWORD")
TIMEZONE = "UTC+6"

# Conversation states
USERNAME, PASSWORD_STATE = range(2)

# Mock data (replace with real implementations)
OTC_ASSETS = [
    "BRLUSD-OTC",
    "USDNGN-OTC",
    "USDCOP-OTC",
    "USDTRY-OTC",
    "USDZAR-OTC",
    "BTCUSD-OTC",
]

STRATEGIES = {
    "1": "RSI + MA50",
    "2": "MACD",
    "3": "Bollinger Bands",
    "4": "Stochastic Oscillator",
    "5": "All Strategies Combined",
}

# ====================== BOT HANDLERS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🚀 <b>𝗦𝗧-𝗤𝗧𝗫 𝗠𝗲𝘁𝗮 𝗣𝗿𝗼 𝗩𝟭.𝟬</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Developed by: @MrStark_Pro
    Channel: @TraderShaanBinary
    Time Zone: {TIMEZONE}
    
    🌟 Please enter username:
    """
    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)
    return USERNAME

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["username"] = update.message.text
    await update.message.reply_text("🔑 Enter Password:")
    return PASSWORD_STATE

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == PASSWORD:
        await update.message.reply_text("✅ Login successful! Use /market to start.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Wrong password. Try /start again.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Login cancelled. Use /start to try again.")
    return ConversationHandler.END

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["1. OTC Market", "2. Real Market"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("📊 Select Market Type:", reply_markup=reply_markup)

async def handle_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if "1" in choice:
        context.user_data["market"] = "OTC"
        assets_list = "\n".join([f"{i+1}. {asset}" for i, asset in enumerate(OTC_ASSETS)])
        await update.message.reply_text(f"📊 Available OTC Assets:\n{assets_list}\nEnter asset numbers (e.g., 1,3,5):")
    elif "2" in choice:
        context.user_data["market"] = "Real"
        await update.message.reply_text("⚠️ Real Market coming soon. Using OTC Market.")
        assets_list = "\n".join([f"{i+1}. {asset}" for i, asset in enumerate(OTC_ASSETS)])
        await update.message.reply_text(f"📊 Available OTC Assets:\n{assets_list}\nEnter asset numbers (e.g., 1,3,5):")
    else:
        await update.message.reply_text("❌ Invalid choice. Try again.")

async def handle_assets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected = update.message.text.split(",")
    selected_assets = [OTC_ASSETS[int(i.strip())-1] for i in selected if i.strip().isdigit()]
    
    context.user_data["assets"] = selected_assets
    strategies_list = "\n".join([f"{k}. {v}" for k, v in STRATEGIES.items()])
    await update.message.reply_text(
        f"📈 Select Signal Type:\n{strategies_list}\nEnter choice (1-5):"
    )

async def handle_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice in STRATEGIES:
        context.user_data["strategy"] = STRATEGIES[choice]
        await update.message.reply_text(
            f"✅ Selected strategy: {STRATEGIES[choice]}\n"
            "📅 Select a day for analysis (1-30 days ago, 0 for today):"
        )
    else:
        await update.message.reply_text("❌ Invalid strategy. Try again.")

async def handle_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = update.message.text
    if day.isdigit() and 0 <= int(day) <= 30:
        context.user_data["day"] = day
        await update.message.reply_text(
            "⏰ Set Signal Time Range (UTC+6)\nStart time (HH:MM):"
        )
    else:
        await update.message.reply_text("❌ Invalid day. Enter 0-30:")

async def handle_start_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["start_time"] = update.message.text
    await update.message.reply_text("⏰ End time (HH:MM):")

async def handle_end_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'assets' not in context.user_data:
        await update.message.reply_text("❌ No assets selected. Please start again with /start and follow the steps.")
        return
    context.user_data["end_time"] = update.message.text
    await update.message.reply_text("📡 Generating signals...")
    
    # Generate mock signals (replace with real signal generation)
    signals = []
    for asset in context.user_data['assets']:
        signals.append(f"• M1 {asset} 05:41 CALL")
        signals.append(f"• M1 {asset} 05:46 PUT")
        signals.append(f"• M1 {asset} 05:51 CALL")

    # Format signal message
    signal_msg = f"""
    𒆜•──❎ <b>𝗙𝗜𝗡𝗔𝗟 ⋅◈⋅ SIGNAL ❎──•𒆜</b>
    ━━━━━━━━━━━━━━━━━━━━━━━
    📆 <i>{datetime.now().strftime('%d/%m/%Y')}</i> 📆
    ━━━━━━━━━━━━━━━━━━━━━━━
    SIGNAL FOR QUOTEX
    
    {TIMEZONE} TIME ZONE
    
    1 MIN SIGNAL, USE 1 STEP MTG MAX
    \n""" + "\n".join(signals) + """
    ━━━━━━━━━━━━━━━━━━━━━━━
    ⚠️ Avoid signals after big candles, doji, below 80%, or gaps
    ━━━━━━━━━━━━━━━━━━━━━━━
    ❤️•──────‼️ ╎@MrStark_Pro╎ ‼️──────•❤️
    """
    context.user_data["last_signal_msg"] = signal_msg

    await update.message.reply_text(signal_msg, parse_mode=ParseMode.HTML)

async def save_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signal_msg = context.user_data.get("last_signal_msg")
    if signal_msg:
        filename = f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(signal_msg)
        await update.message.reply_text(f"✅ Signals saved to file: {filename}")
    else:
        await update.message.reply_text("❌ No signals to save. Generate signals first.")

# ====================== MAIN ======================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Create conversation handler for login
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username)],
            PASSWORD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("market", market))

    # Other conversation handlers - order matters!
    app.add_handler(MessageHandler(filters.Regex(r'^save$'), save_signals))
    app.add_handler(MessageHandler(filters.Regex(r'^\d{1,2}:\d{2}$'), handle_end_time))
    app.add_handler(MessageHandler(filters.Regex(r'^\d{1,2}:\d{2}$'), handle_start_time))
    app.add_handler(MessageHandler(filters.Regex(r'^\d+$'), handle_day))
    app.add_handler(MessageHandler(filters.Regex(r'^[1-5]$'), handle_strategy))
    app.add_handler(MessageHandler(filters.Regex(r'^(\d+,?)+$'), handle_assets))
    app.add_handler(MessageHandler(filters.Regex(r'^[12]\.'), handle_market))

    app.run_polling()

if __name__ == "__main__":
    main()