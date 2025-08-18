from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters
import requests
import os

TG_TOKEN = os.environ.get("TG_TOKEN")
API_KEY = os.environ.get("API_KEY")

POPULAR_CURRENCIES = ["USD", "EUR", "UAH", "GBP", "JPY", "CNY"]

keyboard = [POPULAR_CURRENCIES[:3], POPULAR_CURRENCIES[3:]]
markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I'm bot for the currency exchange. \n\n"
        "Choose currency with buttons, to see course." 
        "Or send me a message in format: 100 USD UAH \n\n"
        "For instruction, enter /help",
        reply_markup=markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Using instruction:\n\n"
        "1. **Accurate convertation**: Send a message in format: `[sum][currency 1][currency 2]`. Example: `100 USD UAH`\n\n"
        "2. **Fast course**: You can use buttons downside. I will show you course of this currency to another popular",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.upper()
    parts = text.split()
    
    if len(parts) == 1 and parts[0] in POPULAR_CURRENCIES:
        base_currency = parts[0]
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
        response = requests.get(url)
        data = response.json()

        if data.get('result') == 'success':
            rates = data['conversion_rates']

            message = f"Course for 1 {base_currency}:\n"
            targets = [curr for curr in POPULAR_CURRENCIES if curr != base_currency]
            for curr in targets:
                message += f"   - {rates.get(curr, '---')} {curr}"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Can't get courses. Try again later.")
    elif len(parts) == 3:
        try:
            amount = float(parts[0])
            base = parts[1]
            target = parts[2]

            url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{base}/{target}"
            response = requests.get(url)
            data = response.json()

            if data.get('result') == 'success':
                rate = data['conversion_rate']
                converted_amount = amount * rate
                await update.message.reply_text(f"{amount} {base} = {converted_amount:.2f} {target}")
            else:
                await update.message.reply_text(f"Can't convert {base} in {target}")
        except ValueError:
            await update.message.reply_text("Sum must be a value. Example `100 USD UAH`.")
        except Exception:
            await update.message.reply_text("Error occured. Check format: `100 USD UAH`.")

    else:
        await update.message.reply_text("Can't understand. Choose currency or send me a message in format `100 USD UAH`.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()

if __name__ == "__main__":
    main()