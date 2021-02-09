# L_System
ОПИСАНИЕ
Это легковесная Scada система для мониторинга сигналов полученных от устройств по протоколу ModBusTCP или ModBusRTU.
Полученные от устройств данные передаются по протоколу Mqtt и с помощью telegram бота.

Для работы НЕОБХОДИМО:
1. Установить mariaDB и в файле config_scada.py вписать параметры подключения к базе данных;
2. В файл config_scada.py вписать chatID того чата куда телеграмм-бот будет направлять сообщения;
3. Заполнить excel файл scada_config.excel своими параметрами, сохранить его в формате csv UTF-8 и загрузить в базу данных.
!!!!Состоит из двух листов "device_list" и "signals_list" таблицы в БД должны иметь такие же названия.!!!!

ОПИСАНИЕ РАБОТЫ ПРОГРАММЫ
Запускаем main.py  и система начинает работать. Логи работы будут сохраняться в log файлы в папке logs.
Система начинает опрос устройств (1 или больше) по протоколу MODBUS и записывает данные в  вашу БД. 
Телеграм бот присылает первое сообщение в ваш ЧАТ ID. 
Mqtt отправляет данные mqtt брокеру.
Комманды для БОТА: data - бот пришлет все актуальные значения сигналов из БД.
Можно запрашивать сигналы по именам которые мы написали в поле "description" таблицы signals_list.
Так же по части имени БОТ может найти сигнал в БД и отправить его в чат.

ИСПОЛЬЗОВАННЫЕ БИБЛИОТЕКИ: 
"easymodbus"
"time"
"loguru"
"paho"
"mariadb"
"date.time"
"sys"
"pyTelegramBotApi"
"random"
ДЛЯ ТЕСТИРОВАНИЯ БЕЗ УСТРОЙСТВ раcкомментировать generator в файле main.py и значения и флаги состояния сигналов будут меняться рандомно.
С помощбю любого mqtt клиента можно следить за изменениями сигналов в режиме реального времени. Так же и с помощью Телеграм бота.
