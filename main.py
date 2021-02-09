import subprocess
import sys
import time
import multiprocessing


def run():
    bot = subprocess.Popen([sys.executable, 'TeleBot.py'])
    time.sleep(5)  # Даем время серверу на запуск
    mqtt = subprocess.Popen([sys.executable, 'mqtt.py'])
    time.sleep(5)
    # Использовать generator для тестирования передачи данных клиенту
    #generator = subprocess.Popen([sys.executable, 'generator.py'])
    time.sleep(5)
    subprocess.Popen([sys.executable, 'polling.py'])
    bot.wait()
    mqtt.wait()
    # generator.wait()


running1 = multiprocessing.Process(target=run)
running2 = multiprocessing.Process(target=run)

if __name__ == '__main__':
    running1.start()
    running1.join()
    running2.start()
    running2.join()

