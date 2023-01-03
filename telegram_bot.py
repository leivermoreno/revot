import logging
import logging.config
import os
from os import path

import yaml
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    ApplicationHandlerStop,
    filters,
)

from mercantil_automation.bank import Bank
from utils import command_handler, message_handler

environment = os.environ.get("PYTHON_ENV")
if environment == "development":
    path_to_file = path.abspath("logging.conf")
    logging.config.fileConfig(path_to_file)

logger = logging.getLogger("main")
logger.debug("Logger successfully configured.")

with open("./secret.yaml", "r", encoding="utf-8") as f:
    data = yaml.load(f, yaml.FullLoader)
    TOKEN = data["bot_token"]
    PASSCODE = data["passcode"]
    logger.debug("Sensitive data loaded.")


# command handlers
@command_handler("start")
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I'm Revot. How can I help you?")


# this command handler verify the passcode the user needs to provide for some commands in order to get access
@command_handler("balance")
async def check_passcode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        passcode = context.args[0]
        assert PASSCODE == passcode
    except (IndexError, AssertionError):
        passcode = context.args[0] if len(context.args) else None
        logger.info(f"Failed passcode verification. Passcode: {passcode}.")
        await update.message.reply_text("Must provide a correct passcode.")
        raise ApplicationHandlerStop  # pylint: disable=raise-missing-from
    finally:
        await update.message.delete()
        await update.message.reply_text("Message deleted for security reasons.")


@command_handler("balance")
async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bank = Bank()
    bank.start_session()
    balance = bank.balance
    await update.message.reply_text(f"Your account balance is BS. {balance}.")


@message_handler(filters.COMMAND)
async def unknown_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command, please try again.")
    raise ApplicationHandlerStop


# handler to dismiss edited commands
@message_handler(filters.UpdateType.EDITED_MESSAGE & filters.COMMAND)
async def edited_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Caught updated command: {update.edited_message.text}")
    raise ApplicationHandlerStop


# handler to log a command's been handled only in development environment
@message_handler(filters.COMMAND)
async def log_handled_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.split(" ")[0]
    logger.info(f'Command "{command}" successfully handled.')


async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.exception(f"An error ocurred processing the update: {update.message.text}")
    await update.effective_message.reply_text(
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
    if environment == "development":
        application.add_handler(log_handled_command, 2)

    application.add_error_handler(handle_error)

    application.run_polling()


main()