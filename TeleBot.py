import telebot
from loguru import logger
from sql import SQL
from config_scada import data_base, data_bot


class MyBot:
    def __init__(self):
        logger.add("logs/bot.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="10MB")
        self.bot_sql = SQL()
        self.bot_sql.connection_to_db(user=data_base['user'],
                                      password=data_base['password'],
                                      host=data_base['host'],
                                      port=data_base['port'],
                                      db_name=data_base['db_name'])
        self.TOKEN = self.bot_sql.get_bot_token()[0][0]
        logger.info("Bots TOKEN is:  ", self.TOKEN)
        self.data_list = list()
        if self.TOKEN is None:
            self.bot_sql.exit_from_db()
            logger.debug("TOKEN unknown")
        else:
            self.bot_sql.exit_from_db()
            logger.info("TOKEN is ready")

    def prepare_data(self):
        self.bot_sql = SQL()
        self.bot_sql.connection_to_db(user=data_base['user'],
                                      password=data_base['password'],
                                      host=data_base['host'],
                                      port=data_base['port'],
                                      db_name=data_base['db_name'])
        self.data_for_send = self.bot_sql.get_data_send_bot()
        self.bot_sql.exit_from_db()
        for tag, value in self.data_for_send:
            self.tag = tag
            self.value = value
            self.data_list.append(f'{self.tag}:  {self.value}')

    def run_bot(self):
        self.bot = telebot.TeleBot(self.TOKEN)
        try:
            self.bot.send_message(data_bot['chat_id'], "Let's Rock!!!")
        except Exception as ex:
            logger.debug(f"cannot receive message to chat {data_bot['chat_id']}", ex)

        @self.bot.message_handler(commands=['start'])
        def start_message(message):
            self.bot.send_message(message.chat.id, 'I AM SCADA BOT')

        @self.bot.message_handler(content_types=['text'])
        def get_messages(message):
            self.prepare_data()
            self.valid_request = False
            if message.text.lower() == "data":
                for i in self.data_list:
                    self.bot.send_message(message.chat.id, i)
                    self.valid_request = True
            else:
                for i in self.data_list:
                    if message.text.lower() in i:
                        self.bot.send_message(message.chat.id, i)
                        self.valid_request = True

            if not self.valid_request:
                self.bot.send_message(message.chat.id, "WRONG REQUEST")

        self.bot.polling()


while True:
    try:
        activate_bot = MyBot()
        activate_bot.run_bot()
    except Exception as e:
        logger.exception(' FAIL Disconnected from telegram', e)
