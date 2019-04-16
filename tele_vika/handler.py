import json
import logging
import os
import traceback

import telegram
from telegram.ext import Dispatcher, CommandHandler, Updater

from tele_vika.conversation import set_conv_handler
from tele_vika.dynamo import insert_spending, get_spending

TOKEN = os.getenv('VIKA_TOKEN')
DEBUG = True

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error_wrapper(handler):
    def wrapper(update, context):
        try:
            return handler(update, context)
        except Exception:
            if DEBUG:
                context.bot.send_message(chat_id=update.message.chat_id, text=traceback.format_exc())

    return wrapper


def wrong_format(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Wrong message format.\n Type /help")


@error_wrapper
def help_handler(update, context):
    help_message = '\n'.join([
        '*Hello:*',
        '    `/start`',
        '',
        '*Note spendings:*',
        '    `/spent 1337 tag`',
        '',
        '*Report spendings:*',
        '    `/report`',
    ])
    context.bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text=help_message)


@error_wrapper
def start_handler(update, context):
    name = update.effective_user.full_name
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Hello, {name}!\nHere is all available commands.")
    help_handler(update, context)


@error_wrapper
def spent_handler(update, context):
    data = update.message.text.split(' ')
    if len(data) != 3:
        return wrong_format(update, context)
    try:
        amount = int(data[1])
    except ValueError:
        return wrong_format(update, context)
    tag = data[2]
    user_id = update.effective_user.id
    insert_spending(user_id, amount, tag)
    response = "*Noted spending:*\n\n"
    response += f"*{tag}:* `{amount}`"

    context.bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text=response)


@error_wrapper
def report_handler(update, context):
    user_id = update.effective_user.id
    data = get_spending(user_id)
    by_tags = {}
    for s in data:
        tag = s['Tag']
        by_tags.setdefault(tag, 0)
        by_tags[tag] += int(s['Amount'])
    response = "*Report:*\n\n"
    for tag, amount in by_tags.items():
        if amount != 0:
            response += f'*{tag}*: `{amount}`\n'
    response += f'\n*Sum:* `{sum(by_tags.values())}`'
    logger.debug(response)
    context.bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text=response)


def setup_dispatcher(dispatcher=None):
    routes = {
        ('start', start_handler),
        ('spent', spent_handler),
        ('help', help_handler),
        ('report', report_handler),
    }
    for command, handler in routes:
        dispatcher.add_handler(CommandHandler(command, handler))


def vika(event, context):
    logger.debug(event)
    update_queue = None
    bot = telegram.Bot(TOKEN)
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    setup_dispatcher(dispatcher=dispatcher)

    update = telegram.Update.de_json(json.loads(event['body']), bot)
    dispatcher.process_update(update)
    return {
        "statusCode": 200,
    }


#########

def vika_dev(token):
    logger.info('init vika dev')
    updater = Updater(token=token, use_context=True)
    setup_dispatcher(updater.dispatcher)

    # set_conv_handler(updater.dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    vika_dev(os.getenv('VIKA_DEV_TOKEN'))
