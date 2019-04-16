from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

SELECT, SPENT, REPORT = range(3)


def cancel():
    return ConversationHandler.END


def test_spend_init(update, context):
    reply_keyboard = [['Spent', 'Report']]

    update.message.reply_text(
        'Hi!',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SELECT


def select_handler(update, context):
    if update.message.text == 'Spent':
        reply_keyboard = [['1', '2', '3']]

        update.message.reply_text(
            'Please select tag!',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return SPENT

    if update.message.text == 'Report':
        return ConversationHandler.END


def make_spent_handler(update, context):
    return ConversationHandler.END


def set_conv_handler(dispatcher):
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('test_spend', test_spend_init)],

            states={
                SELECT: [MessageHandler(Filters.regex('^(Spent|Report)$'), select_handler)],

                SPENT: {MessageHandler(Filters.text, make_spent_handler)},

                # REPORT: [MessageHandler(Filters.text, report_handler)],
            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )
    )

# def start(update, context):
#     keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
#                  InlineKeyboardButton("Option 2", callback_data='2')],
#
#                 [InlineKeyboardButton("Option 3", callback_data='3')]]
#
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     update.message.reply_text('Please choose:', reply_markup=reply_markup)
