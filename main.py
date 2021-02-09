import subprocess
import sys
import time
import multiprocessing
from loguru import logger

def run():
    logger.add("logs/main.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="10MB")
    bot = subprocess.Popen([sys.executable, 'TeleBot.py'])
    time.sleep(5)  # Даем время серверу на запуск
    mqtt = subprocess.Popen([sys.executable, 'mqtt.py'])
    time.sleep(5)
    # Использовать generator для тестирования передачи данных клиенту
    # generator = subprocess.Popen([sys.executable, 'generator.py'])
    # time.sleep(5)
    subprocess.Popen([sys.executable, 'polling.py'])
    bot.wait()
    logger.info("BOT IS READY")
    mqtt.wait()
    logger.info("MQTT IS READY")
    # generator.wait()
    # logger.info("GENERATOR IS READY")


running1 = multiprocessing.Process(target=run)
running2 = multiprocessing.Process(target=run)

if __name__ == '__main__':
    running1.start()
    running1.join()
    running2.start()
    running2.join()

