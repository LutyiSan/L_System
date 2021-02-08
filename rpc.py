from modbus import ModbusDriver
from sql import SQL

class RPC:
    signal_id = str
    value_data = int

    def __init__(self, signal_id, value_data):
        self.sql_set = SQL()
        self.sql_set.connection_to_db('scada')
        self.data_list = self.sql_set.write_command_to_device(signal_id)
        self.device_id = [0][1]
        self.protocol = self.data_list[0][2]
        self.ip_address = self.data_list[0][4]
        self.ip_port = self.data_list[0][5]
        self.unit_id = self.data_list[0][6]
        self.com_port = self.data_list[0][7]
        self.baud_rate = self.data_list[0][8]
        self.stop_bits = self.data_list[0][9]
        self.parity = self.data_list[0][10]
        self.time_out = self.data_list[0][11]
        self.reg_address = self.data_list[1][9]
        self.reg_type = self.data_list[1][10]
        self.value_data = value_data
        self.connect_state = 0

    def do_it(self):
        if self.protocol == "modbusTCP" or self.protocol == "modbusRTU":
            self.modbus_rpc = ModbusDriver(self.ip_address, self.ip_port, self.protocol, self.com_port,
                                           self.baud_rate, self.parity, self.stop_bits, self.time_out,
                                           self.unit_id)
            try:
                self.connect_state = self.modbus_rpc.connect()
            except Exception as e:
                print(e, f'none connection to device: {self.device_id}')

            if self.connect_state == 1:
                try:
                    self.modbus_rpc.writing(self.reg_type, self.reg_address, "write", self.value_data)
                except exit as e:
                    print(e)
                    print(f'cannot write data: {self.value_data} to register: {self.reg_address}'
                          f' to device: {self.device_id}')
