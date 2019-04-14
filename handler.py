import json
import os

import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

from dynamo import insert_spending, get_spending

TOKEN = os.getenv('VIKA_TOKEN')
HELP = """
*Test:*
    `/start`

*Note spendings:*
    `/spent 1337 tag`

*Report spendings:* 
    `/report`
"""


def error(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Wrong message format. Type /help")


def echo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def help_handler(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text=HELP)


def start_handler(update, context):
    name = update.effective_user.full_name
    context.bot.send_message(chat_id=update.message.chat_id, text=f"Hello, {name}!\nHere is all available commands.")
    help_handler(update, context)


def spent_handler(update, context):
    data = update.message.text.split(' ')
    if len(data) != 3:
        return error(update, context)
    try:
        amount = int(data[1])
    except ValueError:
        return error(update, context)
    tag = data[2]
    user_id = update.effective_user.id
    insert_spending(user_id, amount, tag)
    response = "*Noted spending:*\n"
    response += f"*Amount:* _{amount}_\n"
    response += f"*Tag*: _{tag}_\n"

    context.bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text=response)


def report_handler(update, context):
    user_id = update.effective_user.id
    data = get_spending(user_id)
    by_tags = {}
    for s in data:
        tag = s['Tag']
        by_tags.setdefault(tag, 0)
        by_tags[tag] += int(s['Amount'])
    response = "*Report:*\n"
    for k, v in by_tags.items():
        response += f'*{k}*: `{v}`\n'
    response += f'\n*Sum:* `{sum(by_tags.values())}`'
    print(response)
    context.bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text=response)


def setup_dispantcher(dispatcher=None):
    routes = {
        ('start', start_handler),
        ('spent', spent_handler),
        ('help', help_handler),
        ('report', report_handler),
    }
    for command, handler in routes:
        dispatcher.add_handler(CommandHandler(command, handler))

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)


def vika(event, context):
    print(event)
    update_queue = None
    bot = telegram.Bot(TOKEN)
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    setup_dispantcher(dispatcher=dispatcher)

    update = telegram.Update.de_json(json.loads(event['body']), bot)
    dispatcher.process_update(update)
    response = {
        "statusCode": 200,
    }
    return response


if __name__ == '__main__':
    report_handler(None, None)
