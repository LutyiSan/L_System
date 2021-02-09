import mariadb
from loguru import logger
import sys
import time
from datetime import datetime
from config_scada import data_base


class SQL:
    def __init__(self):
        logger.add("logs/sql.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="10MB")
        self.connector = None
        self.cur = None
        self.connect_state = False
        self.signals_list = list()
        self.db_name = str
        self.device_list = list()
        self.mqtt_pub_list = list()
        self.mqtt_sub_list = list()
        self.mqtt_device = list()
        self.vision_list = list()
        self.bot_tokens = list()
        self.bot_topics = list()
        self.data_list = list()
        self.alarm_list = list()
        self.time_stamp = datetime.now()

    def connection_to_db(self, user, password, host, port, db_name):
        while not self.connect_state:
            try:
                self.connector = mariadb.connect(user=data_base['user'],
                                                 password=data_base['password'],
                                                 host=data_base['host'],
                                                 port=data_base['port'],
                                                 database=data_base['db_name'])
                self.cur = self.connector.cursor()
                self.connect_state = True
                logger.info("Data Base is ready to use")
            except Exception as e:
                logger.exception(f'None connection to Data Base {db_name}', e)
                self.connect_state = False
                sys.exit()
            time.sleep(0.5)

    def get_device_list(self):
        try:
            self.cur.execute("SELECT * FROM device_list WHERE state = 'active' ")
            for device in self.cur:
                self.device_list.append(list(device))
            return self.device_list
        except Exception as e:
            logger.debug("Cannot get_device_list", e)

    def get_signals_list(self):
        try:
            self.cur.execute(
                f"SELECT*FROM signals_list WHERE device_id = (SELECT device_id FROM device_list WHERE state = 'active') ")
            for signal in self.cur:
                self.signals_list.append(list(signal))
            return self.signals_list
        except Exception as e:
            logger.debug("Cannot get_signals_list", e)

    def get_gen_signals_list(self):
        try:
            self.cur.execute("SELECT signal_id, server_type FROM signals_list")
            for lst in self.cur:
                self.signals_list.append(list(lst))
            return self.signals_list
        except Exception as e:
            logger.debug("Cannot get_gen_signals_list", e)

    def get_mqtt_params(self):
        try:
            self.cur.execute("SELECT ip_address, ip_port, user_name, password, mqtt_data_prefix FROM device_list WHERE "
                             "protocol = 'mqtt'  ")
            for mqtt in self.cur:
                self.mqtt_device.append(mqtt)
            return self.mqtt_device
        except Exception as e:
            logger.debug("Cannot get_mqtt_params", e)

    def get_mqtt_topics_pub(self):
        try:
            self.cur.execute("SELECT topic_pub, present_value FROM signals_list WHERE topic_pub is not NULL ")
            for topic in self.cur:
                self.mqtt_pub_list.append(topic)
            return self.mqtt_pub_list
        except Exception as e:
            logger.debug("Cannot get_mqtt_topics_pub", e)

    def get_mqtt_topics_sub(self):
        try:
            self.cur.execute(
                "SELECT signal_id, topic_sub, present_value FROM signals_list WHERE topic_sub is not NULL ")
            for topic in self.cur:
                self.mqtt_sub_list.append(topic)
            return self.mqtt_sub_list
        except Exception as e:
            logger.debug("Cannot get_mqtt_topics_sub", e)

    def write_present_value(self, value, status_flag, signal_id):
        self.time_stamp = datetime.now()
        try:
            self.cur.execute(
                f"UPDATE scada.signals_list set present_value = '{value}', status_flag='{status_flag}', time_stamp='{self.time_stamp}' WHERE signal_id = '{signal_id}'")
            logger.info("Done! writing value from modbus device to DB")
            self.connector.commit()
        except Exception as e:
            logger.exception("Can't write value from modbus device to db", e)

    def write_present_value_mqtt(self, value, signal_id):
        self.time_stamp = datetime.now()
        try:
            self.cur.execute(
                f"UPDATE `scada`.`signals_list` SET present_value='{value}', time_stamp ='{self.time_stamp}' WHERE   "
                f"`signal_id`='{signal_id}' ")
            logger.info("Done! writing value from mqtt to DB")
            self.connector.commit()
        except Exception as e:
            logger.exception("CAN'T Done! writing value from mqtt to DB", e)

    def get_bot_token(self):
        try:
            self.cur.execute("SELECT token FROM device_list WHERE protocol = 'telegram_bot' ")
            for token in self.cur:
                self.bot_tokens.append(list(token))
            return self.bot_tokens
        except Exception as e:
            logger.debug('Cannot get_bot_token', e)

    def get_data_send_bot(self):
        try:
            self.cur.execute('SELECT description, present_value FROM signals_list')
            for lst in self.cur:
                self.bot_topics.append(lst)
            return self.bot_topics
        except Exception as e:
            logger.debug('Cannot get_data_send_bot', e)

    def exit_from_db(self):
        self.connector.close()
        logger.info('exit from DB')
