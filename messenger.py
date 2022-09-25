import os
import csv
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters, ConversationHandler, MessageHandler, CallbackQueryHandler
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

form_filename = 'form_responses.csv'
rows = {}
name_idx = -1
tele_handle_idx = -1
locker_floor_idx = -1
locker_number_idx = -1
gift_idx = -1

with open(form_filename, 'r') as f:
    spamreader = csv.reader(f, delimiter=',')
    firstRow = None
    for row in spamreader:
        if(firstRow is None): 
            firstRow = row
            idx = 0
            for header in firstRow:
                h = header.lower()
                print(h)
                if(h == 'name'):
                    name_idx = idx
                elif('telegram' in h):
                    tele_handle_idx = idx
                elif('like' in h):
                    gift_idx = idx
                elif('floor' in h):
                    locker_floor_idx = idx
                elif('locker number' in h):
                    locker_number_idx = idx
                idx += 1
        else:
            rows[row[tele_handle_idx].replace('@', '')] = row

pairs_filename = f'paired_{form_filename}'
pairs = {}
with open(pairs_filename, 'r') as f:
    spamreader = csv.reader(f, delimiter=',')
    for row in spamreader:
        if(row[0] in pairs):
            print(f"{row[0]} seems to have more than one mortal??")
            exit()
        pairs[row[0]] = row[1]

def start(update: Update, context: CallbackContext) -> None:
    username = update.message.from_user.username
    logging.log(logging.DEBUG, pairs)
    if(username not in pairs):
        msg = "your username wasn't in the system! if this is a mistake, please contact @xjinghan or the in-charge"
        update.message.reply_text(msg)
        return
    pair_tele= pairs[username]
    msg = f"""
Hello {username}! 

Thanks for signing up for Angel & Mortal'22!! Here are some information abt your mortal HAVE FUN 🥳🥳🥳

Name: {(rows[pair_tele][name_idx] if name_idx != -1 else "nil")}
Tele Handle: @{pair_tele}
Locker Floor: {(rows[pair_tele][locker_floor_idx] if locker_floor_idx != -1 else "nil")} 
Locker No.: {(rows[pair_tele][locker_number_idx] if locker_number_idx != -1 else "nil")}
Gift preferences: {(rows[pair_tele][gift_idx] if gift_idx != -1 else "nil")}

You may start chatting with them!
Angel Proxy Chat: @dent_anm_angel_bot
Mortal Proxy Chat: @dent_anm_mortal_bot
"""
    update.message.reply_text(msg)
    return
def main():
    updater = Updater(os.environ.get('API_KEY'))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start',start))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
