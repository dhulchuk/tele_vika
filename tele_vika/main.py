import json
import logging
import os

import telegram
from telegram.ext import CommandHandler, Dispatcher, Updater, CallbackQueryHandler

from tele_vika.base_handlers import start_handler, spent_handler, help_handler
from tele_vika.reports import select_report, select_button

TOKEN = os.getenv('VIKA_TOKEN')
DEBUG = True

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def setup_dispatcher(dispatcher=None):
    routes = {
        ('start', start_handler),
        ('spent', spent_handler),
        ('help', help_handler),
        ('report', select_report),
    }
    for command, handler in routes:
        dispatcher.add_handler(CommandHandler(command, handler))

    dispatcher.add_handler(CallbackQueryHandler(select_button))


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

###


def vika_dev(token):
    logger.info('init vika dev')
    updater = Updater(token=token, use_context=True)
    setup_dispatcher(updater.dispatcher)

    # set_conv_handler(updater.dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    vika_dev(os.getenv('VIKA_DEV_TOKEN'))
