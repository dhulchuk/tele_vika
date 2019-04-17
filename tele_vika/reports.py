import datetime
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tele_vika.dynamo import get_spending
from tele_vika.tools import error_wrapper

REPORT_TODAY, REPORT_MONTH = map(str, range(2))


@error_wrapper
def select_report(update, context):
    keyboard = [[InlineKeyboardButton("Report today", callback_data=REPORT_TODAY),
                 InlineKeyboardButton("Report last 30d", callback_data=REPORT_MONTH)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please select:', reply_markup=reply_markup)


@error_wrapper
def select_button(update, context):
    option = update.callback_query.data
    user_id = update.effective_user.id
    if option == REPORT_TODAY:
        response = '*Report for today:*\n\n'
        now = datetime.datetime.now()
        after_d = now.replace(hour=0, minute=0, second=0)
        after = int(after_d.timestamp())
    elif option == REPORT_MONTH:
        response = '*Report for last 30 days:*\n\n'
        now = datetime.datetime.now()
        after_d = now - datetime.timedelta(days=30)
        after = int(after_d.timestamp())
    else:
        raise Exception(f'Wrong option {option}')

    response += format_report(user_id, after)
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode='Markdown', text=response)


def format_report(user_id, after):
    data = get_spending(user_id, after)
    by_tags = {}
    for s in data:
        tag = s['Tag']
        by_tags.setdefault(tag, 0)
        by_tags[tag] += int(s['Amount'])
    response = ""
    for tag, amount in by_tags.items():
        if amount != 0:
            response += f'*{tag}*: `{amount}`\n'
    response += f'\n*Sum:* `{sum(by_tags.values())}`'
    logging.debug(response)
    return response