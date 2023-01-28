from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.filters import BaseFilter


def command_handler(command: str):
    def get_command_handler(callback) -> CommandHandler:
        return CommandHandler(command, callback)

    return get_command_handler


def message_handler(filter: BaseFilter):  # pylint: disable=redefined-builtin
    def get_message_handler(callback) -> MessageHandler:
        return MessageHandler(filter, callback)

    return get_message_handler
