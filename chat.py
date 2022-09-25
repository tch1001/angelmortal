import os
import pika
import csv
from threading import Thread
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, ConversationHandler, MessageHandler, CallbackQueryHandler
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

angels = {}
mortals = {}
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

class Mortal():
    def __init__(self, username: str, angel = None):
        self.username = username
        if(angel is not None):
            self.assign_angel(angel)
    def assign_angel(self, angel):
        assert angel is Angel
        self.angel = angel
        mortals[angel.username] = mortal
        # self.attach_queue()


def queue_name(sender: str, receiver: str) -> str:
    return f'{sender}->{receiver}'

class Angel():
    def __init__(self, username, mortal: Mortal = None):
        self.username = username
        if(mortal is not None):
            self.assign_mortal(mortal)
    def assign_mortal(self, mortal: Mortal):
        self.mortal = mortal
        angels[mortal.username] = angel
        self.attach_queue()

    def to_callback(self, ch, method, properties, body):
        logging.info(f"[x] Received {body} from ch={ch}, method={method}, prop={properties}")

    def from_callback(self, ch, method, properties, body):
        logging.info(f"[x] Received {body} from ch={ch}, method={method}, prop={properties}")

    def attach_queue(self):
        to_channel = connection.channel()
        to_channel_name = queue_name(self.username, self.mortal.username)
        to_channel.queue_declare(queue=to_channel_name)
        to_channel.basic_consume(queue=to_channel_name, on_message_callback=self.to_callback, auto_ack=True)
        to_channel.start_consuming()
        from_channel = connection.channel()
        from_channel_name = queue_name(self.mortal.username, self.username)
        from_channel.queue_declare(queue=from_channel_name)
        from_channel.basic_consume(queue=from_channel_name, on_message_callback=self.from_callback, aufrom_ack=True)
        from_channel.start_consuming()

paired_form_filename = 'paired_form_responses.csv'
name_idx = -1
tele_handle_idx = -1

with open(paired_form_filename, 'r') as f:
    spamreader = csv.reader(f, delimiter=',')
    for row in spamreader:
        angel: Angel = Angel(row[0].replace('@', ''))
        mortal: Mortal = Mortal(row[1].replace('@', ''))
        angel.assign_mortal(mortal)
        mortal.assign_angel(angel)

angel_online_status = {}  # role as an angel
mortal_online_status = {}  # role as a mortal


# check whether my angel is online
def check_angel_online_status(update: Update):
    username = update.message.from_user.username
    mortal_online_status[username] = 'started'
    if(username not in angels):
        msg = f"your username ({username}) wasn't in the list of angels! if this is a mistake, please contact @xjinghan or the in-charge"
        update.message.reply_text(msg)
        return False
    if(angels[username] not in angel_online_status):
        msg = "Sorry! your angel has not started talking to me yet... maybe he/she's busy doing angel stuff?"
        update.message.reply_text(msg)
        return False
    return True


# check whether my angel is online
def check_mortal_online_status(update: Update):
    username = update.message.from_user.username
    angel_online_status[username] = 'started'
    if(username not in mortals):
        msg = f"your username ({username}) wasn't in the list of mortals! if this is a mistake, please contact @xjinghan or the in-charge"
        update.message.reply_text(msg)
        return False
    if(mortals[username] not in mortal_online_status):
        msg = "Sorry! your mortal has not started talking to me yet... maybe he/she's busy doing mortal stuff?"
        update.message.reply_text(msg)
        return False
    return True


def angel_start(update: Update, context: CallbackContext) -> None:
    msg = "angel"
    update.message.reply_text(msg)
    if(not check_angel_online_status(update)):
        return


def angel_status(update: Update, context: CallbackContext) -> None:
    if(not check_angel_online_status(update)):
        return


def mortal_start(update: Update, context: CallbackContext) -> None:
    msg = "mortal"
    update.message.reply_text(msg)
    if(not check_mortal_online_status(update)):
        return


def mortal_status(update: Update, context: CallbackContext) -> None:
    if(not check_mortal_online_status(update)):
        return


def angel_start_bot():
    angel_updater = Updater(os.environ.get('ANGEL_API_KEY'))
    angel_dispatcher = angel_updater.dispatcher
    angel_dispatcher.add_handler(CommandHandler('start', angel_start))
    angel_dispatcher.add_handler(CommandHandler('status', angel_status))
    angel_updater.start_polling()
    angel_updater.idle()


def mortal_start_bot():
    mortal_updater = Updater(os.environ.get('MORTAL_API_KEY'))
    mortal_dispatcher = mortal_updater.dispatcher
    mortal_dispatcher.add_handler(CommandHandler('start', mortal_start))
    mortal_dispatcher.add_handler(CommandHandler('status', mortal_status))
    mortal_updater.start_polling()
    mortal_updater.idle()
