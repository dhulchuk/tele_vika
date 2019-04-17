from tele_vika.dynamo import insert_spending
from tele_vika.tools import error_wrapper, wrong_format


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
