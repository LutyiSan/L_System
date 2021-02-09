from loguru import logger
from modbus import ModbusDriver
from sql import SQL
import time
from config_scada import data_base


class RunTime:
    def __init__(self):
        logger.add("logs/polling.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="1MB")
        self.modbus_client = None
        self.connect_state = 0
        self.scada_db = SQL()
        self.device_list = list()
        self.signal_list = list()
        
    def get_config(self):
        self.scada_db.connection_to_db(user=data_base['user'],
                                       password=data_base['password'],
                                       host=data_base['host'],
                                       port=data_base['port'],
                                       db_name=data_base['db_name'])
        self.device_list = self.scada_db.get_device_list()
        self.signal_list = self.scada_db.get_signals_list()
        self.scada_db.exit_from_db()

    def polling(self):
        while True:
            logger.info("Polling ON")
            for device in self.device_list:
                self.device_id = device[0]
                self.protocol = device[2]
                self.ip_address = device[4]
                self.ip_port = device[5]
                self.unit_id = device[6]
                self.com_port = device[7]
                self.baud_rate = device[8]
                self.stop_bits = device[9]
                self.parity = device[10]
                self.time_out = device[11]
                if self.protocol == "modbusTCP" or self.protocol == "modbusRTU":
                    self.modbus_client = ModbusDriver(self.ip_address, self.ip_port, self.protocol, self.com_port,
                                                      self.baud_rate, self.parity, self.stop_bits, self.time_out,
                                                      self.unit_id)

                    self.connect_state = self.modbus_client.connect()
                    if self.connect_state == 1:
                        for signal in self.signal_list:
                            print(signal)
                            self.s_device_id = signal[1]
                            self.signal_id = signal[0]
                            self.reg_address = signal[8]
                            self.reg_type = signal[9]
                            self.quantity = signal[10]
                            self.bit_string = signal[11]
                            self.word_number = signal[12]
                            self.bit_number = signal[13]
                            self.server_type = signal[14]
                            self.scale = signal[15]

                            if self.device_id == self.s_device_id:
                                self.modbus_client.reading(self.reg_address, self.quantity, self.reg_type,
                                                           self.signal_id,
                                                           self.scale, self.server_type,
                                                           self.bit_string,
                                                           self.word_number, self.bit_number)
                            else:
                                logger.info("Next device")


                    else:
                        logger.debug(f"Connection to device {self.device_id} lost")
                    self.modbus_client.disconnect()
                else:  # ЗДЕСЬ МОГУТ БЫТЬ И ДРУГИЕ ПРОТОКОЛЫ
                    logger.debug("Unknown protocol...")
                    time.sleep(30)


activate_polling = RunTime()
activate_polling.get_config()
activate_polling.polling()
