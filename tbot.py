import json

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.ext import CommandHandler


def txt(update, context):
    update.message.reply_text("Пожалуйста, воспользуйтесь какой-либо командой\n"
                              "Чтобы узнать список и функционал команд, напишите /help\n")


def start(update, context):
    update.message.reply_text(
        "Добро пожаловать! Здесь вы можете получить информацию о ситуации в городе")


def help(update, context):
    update.message.reply_text(
        "Для получения списка команд: /help\n"
        "Для получения информации: /info\n"
        "Для получения информации по ключу: /info_key *key*")


def info(update, context):
    with open('coords.json', 'r') as f:
        data = json.load(f)
    if len(data) == 0:
        update.message.reply_text('На данный момент меток нет')
    else:
        ans = []
        for k, v in data.items():
            ans.append('{}: {}'.format(k, ' ,'.join(v)))
        update.message.reply_text('\n'.join(ans))


def info_key(update, context):
    with open('coords.json', 'r') as f:
        data = json.load(f)
    k = update.message.text[10:]
    print(k)
    if k in data.keys():
        update.message.reply_text('{}: {}'.format(k, ' ,'.join(data[k])))
    else:
        update.message.reply_text('Такой метки не существует')


def main():
    updater = Updater("1748358061:AAG03j7QuYQd_c6weaXd00lK8SDbUg4Aklg", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("info_key", info_key))
    text_handler = MessageHandler(Filters.text, txt)
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()