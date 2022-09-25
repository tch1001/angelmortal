import queue
from typing import Dict
import os
import csv
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from threading import Thread

import redis

client = redis.Redis(decode_responses=True)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()


def queue_name(A: str, B: str) -> str:
    if(A > B):
        A, B = B, A
    return f'{A}-{B}'

class Duplex():
    def __init__(self, A: str, B: str):
        # A is primary (first person pov)
        # B is secondary
        self.A : str = A
        self.B : str = B
        if(self.A > self.B):
            self.reverse = True # primary is the right guy
        else:
            self.reverse = False # primary is the left guy
        # queue name is alphabetical, direction is given by LR/RL
        self.LR_queue_name = queue_name(A,B)+'_LR'
        self.RL_queue_name = queue_name(A,B)+'_RL'
    def send(self, text): # send from primary to secondary
        if(self.reverse): # primary is right
            # send from right (primary) to left
            client.rpush(self.RL_queue_name, text)
        else:
            client.rpush(self.LR_queue_name, text)
    def recv(self): # receive from secondary to primary
        if(self.reverse): # primary is right
            return client.lpop(self.LR_queue_name)
        else: # primary is left
            return client.lpop(self.RL_queue_name)
    def set_ready(self):
        if(self.reverse): # primary is right
            # means right is ready
            client.set(f'{self.RL_queue_name}_status', "ready")
        else:
            client.set(f'{self.LR_queue_name}_status', "ready")
    def get_ready(self):
        if(self.reverse): # primary is right
            return client.get(f'{self.RL_queue_name}_status') is not None
        else:
            return client.get(f'{self.LR_queue_name}_status') is not None

class User():
    def __init__(self, username: str):
        self.username = username
        self.ready = False
        self.duplex : Duplex = None
        self.convo = None

    def set_ready(self):
        self.duplex.set_ready()

    def user_ready(self):
        return self.duplex.get_ready()

    def check_messages(self, update : Update = None):
        msg = self.duplex.recv()
        if update is None: update = self.convo
        if(msg is None):
            update.message.reply_text(f'no new messages')
            return
        update.message.reply_text(msg)

    # def wait_for_message(self):
    #     while True:
    #         message = self.sub.get_message()
    #         if message:
    #             print(f'angel {self.username} recv {message["data"]}')
    
    def send_message(self, text: str):
        self.duplex.send(text)

    def attach_queue(self):
        self.sub = client.pubsub()
        # self.sub.subscribe(f'{self.queue_name}_notif')
        # Thread(target = self.wait_for_message).start()

class Mortal(User):
    def __init__(self, username: str, angel = None):
        super().__init__(username)
        if(angel is not None):
            self.assign_angel(angel)

    def assign_angel(self, angel):
        assert type(angel) is Angel
        self.angel = angel
        self.duplex = Duplex(self.username, self.angel.username)

    def angel_ready(self):
        if(self.angel is None):
            return False
        if(not self.angel.user_ready()):
            return False
        return True

class Angel(User):
    def __init__(self, username, mortal: Mortal = None):
        self.username = username
        self.sub = None
        if(mortal is not None):
            self.assign_mortal(mortal)

    def mortal_ready(self):
        if(self.mortal is None):
            return False
        if(not self.mortal.user_ready()):
            return False
        return True

    def assign_mortal(self, mortal: Mortal):
        self.mortal = mortal
        self.duplex = Duplex(self.username, self.mortal.username)

paired_form_filename = 'paired_form_responses.csv'
name_idx = -1
tele_handle_idx = -1

angels : Dict[str, Angel] = {}
mortals : Dict[str, Mortal] = {}

with open(paired_form_filename, 'r') as f:
    spamreader = csv.reader(f, delimiter=',')
    for row in spamreader:
        angel: Angel = Angel(row[0].replace('@', ''))
        mortal: Mortal = Mortal(row[1].replace('@', ''))
        angel.assign_mortal(mortal)
        mortal.assign_angel(angel)
        angels[angel.username] = angel
        mortals[mortal.username] = mortal
logging.info(angels)
logging.info(mortals)

# check whether my angel is online (i am mortal)
def check_angel_online_status(update: Update, quiet = False):
    username = update.message.from_user.username
    if(username in mortals):
        mortals[username].set_ready()
    else:
        msg = f"your username ({username}) wasn't in the list of mortals! if this is a mistake, please contact @xjinghan or the in-charge"
        update.message.reply_text(msg)
        return False
    if(not mortals[username].angel_ready()):
        msg = "Sorry! your angel has not started talking yet... maybe he/she's busy doing angel stuff?"
        update.message.reply_text(msg)
        return False
    if(not quiet):
        msg = f"you may start chatting with your angel! i'll let yall be ;)"
        update.message.reply_text(msg)
    return True

# check whether my mortal is online
def check_mortal_online_status(update: Update, quiet = False):
    username = update.message.from_user.username
    if(username in angels):
        angels[username].set_ready()
    else:
        msg = f"your username ({username}) wasn't in the list of angels! if this is a mistake, please contact @xjinghan or the in-charge"
        update.message.reply_text(msg)
        return False
    if(not angels[username].mortal_ready()):
        msg = "Sorry! your mortal has not started talking yet... maybe he/she's busy doing mortal stuff?"
        update.message.reply_text(msg)
        return False
    if(not quiet):
        msg = f"you may start chatting with your mortal {angels[username].mortal.username}! i'll let yall be ;)"
        update.message.reply_text(msg)
    return True

def angel_start(update: Update, context) -> None:
    if(not check_angel_online_status(update)):
        return
    username = update.message.from_user.username
    mortals[username].convo = update

def mortal_start(update: Update, context) -> None:
    if(not check_mortal_online_status(update)):
        return
    username = update.message.from_user.username
    angels[username].convo = update

def angel_message_handler(update: Update, context):
    if(not check_angel_online_status(update, quiet = False)):
        return
    user = update.message.from_user.username
    mortals[user].send_message(update.message.text)

def mortal_message_handler(update: Update, context):
    if(not check_mortal_online_status(update, quiet = False)):
        return
    user = update.message.from_user.username
    angels[user].send_message(update.message.text)

def angel_check(update: Update, context):
    user = update.message.from_user.username
    mortals[user].check_messages(update)

def mortal_check(update: Update, context):
    user = update.message.from_user.username
    angels[user].check_messages(update)

def angel_start_bot():
    angel_updater = Updater(os.environ.get('ANGEL_API_KEY'))
    angel_dispatcher = angel_updater.dispatcher
    angel_dispatcher.add_handler(CommandHandler('start', angel_start))
    angel_dispatcher.add_handler(CommandHandler('check', angel_check))
    angel_dispatcher.add_handler(MessageHandler(Filters.text, angel_message_handler))
    angel_updater.start_polling()
    angel_updater.idle()
    for a in angels:
        angels[a].attach_queue()


def mortal_start_bot():
    mortal_updater = Updater(os.environ.get('MORTAL_API_KEY'))
    mortal_dispatcher = mortal_updater.dispatcher
    mortal_dispatcher.add_handler(CommandHandler('start', mortal_start))
    mortal_dispatcher.add_handler(CommandHandler('check', mortal_check))
    mortal_dispatcher.add_handler(MessageHandler(Filters.text, mortal_message_handler))
    mortal_updater.start_polling()
    mortal_updater.idle()
    for m in mortals:
        mortals[m].attach_queue()