import os
import telebot
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY")

if not TOKEN:
    raise ValueError("BOT_TOKEN ما كاينش فـ.env")

bot = telebot.TeleBot(TOKEN)
PREMIUM_USERS = []
ADMIN_ID = 0

def check_premium(func):
    def wrapper(message):
        if message.from_user.id not in PREMIUM_USERS and message.from_user.id!= ADMIN_ID:
            bot.reply_to(message, "❌ هاد الميزة للمشتركين Pro فقط.\nاستعمل /buy للاشتراك")
            return
        return func(message)
    return wrapper

def get_eth_balance(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_KEY}"
    try:
        r = requests.get(url, timeout=10).json()
        if r['status'] == '1': return int(r['result']) / 10**18
    except: pass
    return None

def get_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
    try:
        r = requests.get(url, timeout=10).json()
        return r.get(symbol.lower(), {}).get('usd')
    except: return None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👻 Blockchain Guard خدام\n/price BTC - سعر العملة\n/wallet_eth 0x... - فحص محفظة Pro")

@bot.message_handler(commands=['price'])
def handle_price(message):
    try: symbol = message.text.split()[1]
    except: bot.reply_to(message, "❌ /price BTC"); return
    price = get_price(symbol)
    if price: bot.reply_to(message, f"💰 {symbol.upper()}: ${price:,.2f}")
    else: bot.reply_to(message, "❌ ما لقيتهاش")

@bot.message_handler(commands=['wallet_eth'])
@check_premium
def handle_wallet(message):
    try: address = message.text.split()[1]
    except: bot.reply_to(message, "❌ /wallet_eth 0x..."); return
    balance = get_eth_balance(address)
    if balance is None: bot.reply_to(message, "❌ خطأ"); return
    bot.reply_to(message, f"📊 المحفظة: {balance:.4f} ETH")

@bot.message_handler(commands=['addpremium'])
def add_premium(message):
    global ADMIN_ID
    if ADMIN_ID == 0: ADMIN_ID = message.from_user.id
    if message.from_user.id!= ADMIN_ID: return
    try:
        user_id = int(message.text.split()[1])
        PREMIUM_USERS.append(user_id)
        bot.reply_to(message, f"✅ تضاف {user_id} للـ Pro")
    except: bot.reply_to(message, "❌ /addpremium 123456789")

if __name__ == "__main__":
    print("البوت خدام...")
    bot.infinity_polling()
