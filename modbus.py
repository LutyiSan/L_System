from easymodbus.modbusClient import *
import time
from loguru import logger
from sql import SQL
from config_scada import data_base


class ModbusDriver:
    def __init__(self, ip_address, ip_port, protocol, com_port,
                 baud_rate, parity, stop_bits, time_out, unit_id):
        logger.add("logs/modbus.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="10MB")
        self.connectState = 0
        self.modbus_tcp_client = ModbusClient(ip_address, ip_port)
        self.modbus_rtu_client = ModbusClient(com_port)
        self.modbus_rtu_client.parity = parity
        self.modbus_rtu_client.unitidentifier = unit_id
        self.modbus_rtu_client.baudrate = baud_rate
        self.modbus_rtu_client.stopbits = stop_bits
        self.modbus_rtu_client.timeout = time_out
        self.modbus_client = None
        self.save_float_data = None
        self.save_data = list()
        self.read_data = None
        self.data_conv_bin = None
        self.server_data = None
        self.protocol = protocol
        self.retry = 5
        self.status_flag = 'fault'
        self.connect_state = False
        self.ip = ip_address
        self.unit_id = unit_id

    def connect(self):
        if self.protocol == "modbusTCP":
            self.connect_state = False

            while not self.connectState and self.retry <= 5:
                self.retry += 1
                try:
                    self.modbus_tcp_client.connect()
                    self.connect_state = True
                except Exception as e:
                    logger.debug(f'No answer from device {self.ip} trying: {self.retry}', e)
                    try:
                        self.modbus_tcp_client.close()
                    except Exception as e:
                        logger.debug(f'None connection to device {self.ip}', e)
                    time.sleep(0.5)
            if not self.connect_state:
                logger.info(f'Cannot connecting to device {self.ip}')
            else:
                logger.info(f"ModbusTCP connecting to {self.ip} READY")
                self.modbus_client = self.modbus_tcp_client
        elif self.protocol == "modbusRTU":
            self.connect_state = False
            while not self.connectState and self.retry <= 5:
                self.retry += 1
                try:
                    self.modbus_rtu_client.connect()
                    self.connect_state = True
                except Exception as e:
                    logger.info(f'No answer from device id: {self.unit_id} trying: {self.retry}', e)
                    try:
                        self.modbus_rtu_client.close()
                    except Exception as e:
                        logger.info(f'No answer from device id: {self.unit_id} trying: {self.retry}', e)
                    time.sleep(0.5)
            if not self.connect_state:
                logger.info(f'Cannot connecting to device id: {self.unit_id}')
            else:
                logger.info(f"ModbusTCP connecting device id: {self.unit_id} READY")
                self.modbus_client = self.modbus_rtu_client
        return self.connect_state

    # noinspection PyArgumentList
    def reading(self, reg_address, quantity, reg_type, signal_id,
                scale, server_type, bit_string, word_number, bit_number):
        if self.connect_state:
            print(reg_address, quantity, reg_type)
            try:
                if reg_type == "holding":
                    self.read_data = self.modbus_client.read_holdingregisters(reg_address, quantity)
                    if word_number is not None:
                        self.save_data = self.read_data[word_number]
                    else:
                        self.save_data_fin = self.read_data[0]
                        if bit_number is not None and bit_string == "normal":
                            self.save_data_bin = bin(self.save_data)
                            self.save_data_fin = self.save_data_bin[bit_number + 2]
                        elif bit_number is not None and bit_string == "reverse":
                            self.save_data_bin = bin(self.save_data[0])[::-1]
                            self.save_data_fin = self.save_data_bin[bit_number + 2]

                elif reg_type == "input":
                    self.read_data = self.modbus_client.read_inputregisters(reg_address, quantity)
                    if word_number is not None:
                        self.save_data = self.read_data[word_number]
                    else:
                        self.save_data_fin = self.read_data[0]
                        if bit_number is not None and bit_string == "normal":
                            self.save_data_bin = bin(self.save_data)
                            self.save_data_fin = self.save_data_bin[bit_number + 2]
                        elif bit_number is not None and bit_string == "reverse":
                            self.save_data_bin = bin(self.save_data[0])[::-1]
                            self.save_data_fin = self.save_data_bin[bit_number + 2]
                        else:
                            pass
                elif reg_type == "coils":
                    self.read_data = self.modbus_client.read_coils(reg_address, quantity)
                    if word_number is not None:
                        self.save_data = self.read_data[word_number]
                    else:
                        self.save_data_fin = self.read_data[0]
                        if bit_number is not None and bit_string == "normal":
                            self.save_data_bin = bin(self.save_data)
                            self.save_data_fin = self.save_data_bin[bit_number + 2]
                        elif bit_number is not None and bit_string == "reverse":
                            self.save_data_bin = bin(self.save_data[0])[::-1]
                            self.save_data_fin = self.save_data_bin[bit_number + 2]
                        else:
                            pass

                elif reg_type == "discrete":
                    self.read_data = self.modbus_client.read_discreteinputs(reg_address, quantity)
                    if word_number is not None:
                        self.save_data = self.read_data[word_number]
                    else:
                        self.save_data_fin = self.read_data[0]
                        if bit_number is not None and bit_string == "normal":
                            self.save_data_bin = bin(self.save_data)
                            self.save_data_fin = self.save_data_bin[bit_number + 2]
                        elif bit_number is not None and bit_string == "reverse":
                            self.save_data_bin = bin(self.save_data[0])[::-1]
                            self.save_data_fin = self.save_data_bin[bit_number + 2]
                        else:
                            pass

                elif reg_type == "holding" and server_type == "float":
                    self.read_data = convert_registers_to_float(
                        self.modbus_client.read_holdingregisters(reg_address, quantity))
                    self.save_float_data = self.read_data[0]
                    self.save_data_fin = self.save_float_data

                elif reg_type == "input" and server_type == "float":
                    self.read_data = convert_registers_to_float(
                        self.modbus_client.read_holdingregisters(reg_address, quantity))
                    self.save_float_data = self.read_data[0]
                    self.save_data_fin = self.save_float_data

                else:
                    logger.debug(f'Fail reading from register {reg_address}')

                if server_type == 'int' or server_type == 'float' or server_type == 'uint':
                    self.server_data = str(self.save_data_fin / scale)
                elif server_type == 'bool':
                    if self.save_data_fin >= 1:
                        self.server_data = "active"
                    else:
                        self.server_data = 'inactive'
                else:
                    logger.debug('Wrong value server_type!!')

                # ЭТО ФУНКЦИЯ ДЛЯ СОХРАНЕНИЯ ДАННЫХ
                self.status_flag = 'normal'
                sql_modbus = SQL()
                sql_modbus.connection_to_db(user=data_base['user'],
                                            password=data_base['password'],
                                            host=data_base['host'],
                                            port=data_base['port'],
                                            db_name=data_base['db_name'])
                sql_modbus.write_present_value(str(self.server_data), self.status_flag, str(signal_id))
                sql_modbus.exit_from_db()
            except Exception as e:
                sql_modbus = SQL()
                sql_modbus.connection_to_db(user=data_base['user'],
                                            password=data_base['password'],
                                            host=data_base['host'],
                                            port=data_base['port'],
                                            db_name=data_base['db_name'])
                sql_modbus.write_present_value('none', 'fault', str(signal_id))
                sql_modbus.exit_from_db()
                logger.debug(f'Fail reading from register {reg_address}', e)

        else:
            try:
                self.modbus_client.close()
            except Exception as e:
                logger.exception('None connecting to device', e)

    def writing(self, reg_type, reg_address, action, value_data, data_type):
        if self.connect_state == 1:
            try:
                if reg_type == "coils" and action == "write":
                    self.modbus_client.write_single_coil(reg_address, value_data)

                elif reg_type == "holding" and action == "write":
                    self.modbus_client.write_single_register(reg_address, value_data)

                elif reg_type == "multi_coils" and action == "write":
                    self.modbus_client.write_multiple_coils(reg_address, [value_data])

                elif reg_type == "holding" and action == "WRITE" and data_type == 'float':
                    self.modbus_client.write_multiple_registers(reg_address, convert_float_to_two_registers(value_data))

                else:
                    logger.info('Wrong request for writing')
            except Exception as e:
                logger.debug("Cannot write data to device", e)

    def disconnect(self):
        try:
            self.modbus_client.close()
            logger.info("Disconnected for end of polling this device")
        except Exception as e:
            logger.exception('Cant exiting device', e)
