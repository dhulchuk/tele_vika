import traceback

DEBUG = True


def error_wrapper(handler):
    def wrapper(update, context):
        try:
            return handler(update, context)
        except Exception:
            if DEBUG:
                context.bot.send_message(chat_id=update.effective_chat.id, text=traceback.format_exc())

    return wrapper


def wrong_format(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="Wrong message format.\n Type /help")
