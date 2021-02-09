import paho.mqtt.client as mqtt
from loguru import logger
import time
from sql import SQL
from config_scada import data_base


class MyMQTTClass(mqtt.Client):
    def __init__(self):
        super().__init__()
        logger.add("logs/mqtt.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="10MB")
        self.connect_state = False
        self.mqtt_sql = SQL()
        self.mqtt_sql.connection_to_db(user=data_base['user'],
                                       password=data_base['password'],
                                       host=data_base['host'],
                                       port=data_base['port'],
                                       db_name=data_base['db_name'])
        self.connect_params = self.mqtt_sql.get_mqtt_params()

        self.mqtt_sql.exit_from_db()
        print(self.connect_params)
        self.broker_address = self.connect_params[0][0]

        self.port = self.connect_params[0][1]

        self.user = self.connect_params[0][2]
        self.password = self.connect_params[0][3]
        self.user_data = self.connect_params[0][4]
        self.sub_data = None
        self.write_value = str
        # self.client.username_pw_set(self.user, self.password)
        logger.info(self.connect_params)
        time.sleep(1)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connection is ready")
            time.sleep(1)
        else:
            logger.info("Connection FAULT")

    def on_message(self, client, userdata, message):
        time.sleep(0.11)
        self.write_value = str(message.payload.decode("utf-8"))
        logger.info("received message =", str(message.payload.decode("utf-8")))

    def on_publish(self, client, obj, mid):
        logger.info("mid: " + str(mid))

    def on_subscribe(self, client, obj, mid, granted_qos):
        logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, client, obj, level, string):
        logger.info(string)

    def run(self):
        while not self.connect_state:
            try:
                self.connect(host=self.broker_address, port=self.port)
                self.connect_state = True
            except Exception as ex:
                logger.exception("None connecting to MQTT", ex)
                self.connect_state = False
                time.sleep(1)
        if self.connect_state:
            self.loop_start()
            while True:
                try:
                    self.mqtt_sql = SQL()
                    self.mqtt_sql.connection_to_db(user=data_base['user'],
                                                   password=data_base['password'],
                                                   host=data_base['host'],
                                                   port=data_base['port'],
                                                   db_name=data_base['db_name'])
                    self.pub_list = self.mqtt_sql.get_mqtt_topics_pub()
                    self.sub_list = self.mqtt_sql.get_mqtt_topics_sub()
                    self.mqtt_sql.exit_from_db()
                    for topic, value in self.pub_list:
                        self.publish(f'{self.user_data}/{str(topic)}', str(value))
                        time.sleep(0.01)
                    for topic in self.sub_list:
                        if topic[1] != '':
                            print(topic)
                            self.sub_data = self.subscribe(topic[1])
                            self.mqtt_sql.write_present_value_mqtt(str(self.write_value), topic[0])
                            time.sleep(0.01)

                except Exception as e:
                    logger.debug("something wrong with mqtt", e)
                    self.disconnect()
                    self.loop_stop()
                time.sleep(5.0)
        else:
            logger.info("Can't connecting to broker")
            self.mqtt_sql.exit_from_db()

        # rc = 0
        # while rc == 0:
        # rc = self.loop()
        # return rc


# If you want to use a specific client id, use
# mqttc = MyMQTTClass("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
client = MyMQTTClass()
client.run()
