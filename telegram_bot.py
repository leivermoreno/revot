import yaml
from mercantil_automation import Bank
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ApplicationHandlerStop,
    ContextTypes,
    filters,
)
from utils import command_handler, message_handler

with open("./secret.yaml", "r", encoding="utf-8") as f:
    data = yaml.load(f, yaml.FullLoader)
    TOKEN = data["bot_token"]
    PASSCODE = data["passcode"]


# command handlers
@command_handler("start")
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I'm Revot. How can I help you?")


# verify passcode needed to access other commands
@command_handler("balance")
async def check_passcode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        passcode = context.args[0]
        if PASSCODE != passcode:
            raise ValueError("Invalid passcode.")
    except (IndexError, ValueError):
        passcode = context.args[0] if len(context.args) else None
        await update.message.reply_text("Must provide a correct passcode.")
        raise ApplicationHandlerStop  # pylint: disable=raise-missing-from
    finally:
        await update.message.delete()
        await update.message.reply_text("Message deleted for security reasons.")


@command_handler("balance")
async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Getting balance, please wait.")
    bank = Bank()
    bank.start_session()
    balance = bank.balance
    bank.close()
    await update.message.reply_text(f"Your account balance is BS. {balance}.")


# handle unknown commands
@message_handler(filters.COMMAND)
async def unknown_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command, please try again.")
    raise ApplicationHandlerStop


# catch edited commands to avoid being re-handled
@message_handler(filters.UpdateType.EDITED_MESSAGE & filters.COMMAND)
async def edited_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raise ApplicationHandlerStop


async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "An error ocurred processing your command, please try again."
    )
    raise ApplicationHandlerStop


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    handlers = {
        0: [edited_message_handler, check_passcode_handler],
        1: [start_handler, balance_handler, unknown_command_handler],
    }
    application.add_handlers(handlers)
    application.add_error_handler(handle_error)
    application.run_polling()


main()
