import random
import time
from loguru import logger
from sql import SQL
from config_scada import data_base


class GEN:
    def __init__(self):
        logger.add("logs/generator.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="1MB")
        self.gen_sql = SQL()
        self.gen_sql.connection_to_db(user=data_base['user'],
                                      password=data_base['password'],
                                      host=data_base['host'],
                                      port=data_base['port'],
                                      db_name=data_base['db_name'])
        self.signals = self.gen_sql.get_gen_signals_list()

    def run_gen(self):
        while True:
            for signal in self.signals:
                self.signal_id = signal[0]
                self.s_type = signal[1]
                if self.s_type == 'int':
                    self.present_value = random.randint(7, 100)
                elif self.s_type == 'bool':
                    self.present_value = random.choice(['active', 'inactive'])
                self.flag = random.choice(['normal', 'fault', 'alarm'])
                self.gen_sql.write_present_value(self.present_value, self.flag, self.signal_id)
            logger.info('generator post data to DB')
            time.sleep(5)

activate_generator = GEN()
activate_generator.run_gen()
