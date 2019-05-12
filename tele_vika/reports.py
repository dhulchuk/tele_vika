import datetime
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tele_vika.dynamo import get_spending
from tele_vika.tools import error_wrapper

PERIOD_SPLIT_DATE = 15

REPORT_TODAY, REPORT_WEEK, REPORT_MONTH, REPORT_CURRENT_PERIOD = map(str, range(4))


@error_wrapper
def select_report(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Report today", callback_data=REPORT_TODAY),
            InlineKeyboardButton("Report this week", callback_data=REPORT_WEEK)
        ],
        [
            InlineKeyboardButton("Report last 30d", callback_data=REPORT_MONTH),
            InlineKeyboardButton(f"Report current {PERIOD_SPLIT_DATE} to {PERIOD_SPLIT_DATE}",
                                 callback_data=REPORT_CURRENT_PERIOD)
        ]
    ]
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
    elif option == REPORT_WEEK:
        response = '*Report for this week:*\n\n'
        now = datetime.datetime.now()
        after_d = now - datetime.timedelta(days=now.weekday())
        after_d = after_d.replace(hour=0, minute=0, second=0)
    elif option == REPORT_MONTH:
        response = '*Report for last 30 days:*\n\n'
        now = datetime.datetime.now()
        after_d = now - datetime.timedelta(days=30)
    elif option == REPORT_CURRENT_PERIOD:
        response = '*Report after the 15th:*\n\n'
        now = datetime.datetime.now()
        if now.day >= 15:
            after_d = now.replace(day=15, hour=0, minute=0, second=0)
        else:
            after_d = now.replace(day=1)
            after_d = after_d - datetime.timedelta(days=2)
            after_d = after_d.replace(day=15, hour=0, minute=0, second=0)
    else:
        raise Exception(f'Wrong option {option}')

    after = int(after_d.timestamp())
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
