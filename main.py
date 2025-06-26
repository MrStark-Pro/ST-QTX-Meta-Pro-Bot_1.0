import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
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
def start(update: Update, context: CallbackContext):
    welcome_msg = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🚀 <b>𝗦𝗧-𝗤𝗧𝗫 𝗠𝗲𝘁𝗮 𝗣𝗿𝗼 𝗩𝟭.𝟬</b>
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Developed by: @MrStark_Pro
    Channel: @TraderShaanBinary
    Time Zone: {TIMEZONE}
    
    🌟 Please enter username:
    """
    update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)
    return USERNAME

def handle_username(update: Update, context: CallbackContext):
    context.user_data["username"] = update.message.text
    update.message.reply_text("🔑 Enter Password:")
    return PASSWORD_STATE

def handle_password(update: Update, context: CallbackContext):
    if update.message.text == PASSWORD:
        update.message.reply_text("✅ Login successful! Use /market to start.")
        return ConversationHandler.END
    else:
        update.message.reply_text("❌ Wrong password. Try /start again.")
        return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Login cancelled. Use /start to try again.")
    return ConversationHandler.END

def market(update: Update, context: CallbackContext):
    keyboard = [["1. OTC Market", "2. Real Market"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text("📊 Select Market Type:", reply_markup=reply_markup)

def handle_market(update: Update, context: CallbackContext):
    choice = update.message.text
    if "1" in choice:
        context.user_data["market"] = "OTC"
        assets_list = "\n".join([f"{i+1}. {asset}" for i, asset in enumerate(OTC_ASSETS)])
        update.message.reply_text(f"📊 Available OTC Assets:\n{assets_list}\nEnter asset numbers (e.g., 1,3,5):")
    elif "2" in choice:
        context.user_data["market"] = "Real"
        update.message.reply_text("⚠️ Real Market coming soon. Using OTC Market.")
        assets_list = "\n".join([f"{i+1}. {asset}" for i, asset in enumerate(OTC_ASSETS)])
        update.message.reply_text(f"📊 Available OTC Assets:\n{assets_list}\nEnter asset numbers (e.g., 1,3,5):")
    else:
        update.message.reply_text("❌ Invalid choice. Try again.")

def handle_assets(update: Update, context: CallbackContext):
    selected = update.message.text.split(",")
    selected_assets = [OTC_ASSETS[int(i.strip())-1] for i in selected if i.strip().isdigit()]
    
    context.user_data["assets"] = selected_assets
    strategies_list = "\n".join([f"{k}. {v}" for k, v in STRATEGIES.items()])
    update.message.reply_text(
        f"📈 Select Signal Type:\n{strategies_list}\nEnter choice (1-5):"
    )

def handle_strategy(update: Update, context: CallbackContext):
    choice = update.message.text
    if choice in STRATEGIES:
        context.user_data["strategy"] = STRATEGIES[choice]
        update.message.reply_text(
            f"✅ Selected strategy: {STRATEGIES[choice]}\n"
            "📅 Select a day for analysis (1-30 days ago, 0 for today):"
        )
    else:
        update.message.reply_text("❌ Invalid strategy. Try again.")

def handle_day(update: Update, context: CallbackContext):
    day = update.message.text
    if day.isdigit() and 0 <= int(day) <= 30:
        context.user_data["day"] = day
        update.message.reply_text(
            "⏰ Set Signal Time Range (UTC+6)\nStart time (HH:MM):"
        )
    else:
        update.message.reply_text("❌ Invalid day. Enter 0-30:")

def handle_start_time(update: Update, context: CallbackContext):
    context.user_data["start_time"] = update.message.text
    update.message.reply_text("⏰ End time (HH:MM):")

def handle_end_time(update: Update, context: CallbackContext):
    if 'assets' not in context.user_data:
        update.message.reply_text("❌ No assets selected. Please start again with /start and follow the steps.")
        return
    context.user_data["end_time"] = update.message.text
    update.message.reply_text("📡 Generating signals...")
    
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

    update.message.reply_text(signal_msg, parse_mode=ParseMode.HTML)

def save_signals(update: Update, context: CallbackContext):
    signal_msg = context.user_data.get("last_signal_msg")
    if signal_msg:
        filename = f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(signal_msg)
        update.message.reply_text(f"✅ Signals saved to file: {filename}")
    else:
        update.message.reply_text("❌ No signals to save. Generate signals first.")

# ====================== MAIN ======================
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Create conversation handler for login
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(Filters.text & ~Filters.command, handle_username)],
            PASSWORD_STATE: [MessageHandler(Filters.text & ~Filters.command, handle_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("market", market))

    # Other conversation handlers - order matters!
    dp.add_handler(MessageHandler(Filters.regex(r'^save$'), save_signals))
    dp.add_handler(MessageHandler(Filters.regex(r'^\d{1,2}:\d{2}$'), handle_end_time))
    dp.add_handler(MessageHandler(Filters.regex(r'^\d{1,2}:\d{2}$'), handle_start_time))
    dp.add_handler(MessageHandler(Filters.regex(r'^\d+$'), handle_day))
    dp.add_handler(MessageHandler(Filters.regex(r'^[1-5]$'), handle_strategy))
    dp.add_handler(MessageHandler(Filters.regex(r'^(\d+,?)+$'), handle_assets))
    dp.add_handler(MessageHandler(Filters.regex(r'^[12]\.'), handle_market))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()