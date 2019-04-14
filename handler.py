import json
import os

import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv('VIKA_TOKEN')


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Hello, Darling!!")


def echo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def vika(event, context):
    bot = telegram.Bot(TOKEN)
    update_queue = None
    print(event)
    dispatcher = Dispatcher(bot, update_queue, use_context=True)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    update = telegram.Update.de_json(json.loads(event['body']), bot)

    dispatcher.process_update(update)

    body = {
        "message": f"Hello Kitty! ^_^",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
