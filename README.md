# **Homework bot** for Telegram
![Python](https://img.shields.io/badge/-Python-191970?style=flat&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/-Telegram-4682B4?style=flat&logo=telegram&logoColor=white)


## Описание проекта
Бот, отслеживаюищий статус проверки домашнего задания от **Яндекс Практикума**.
## Регистрируем бота
В окне поиска контактов в **Telegram** введите **@BotFather** и начните с ним диалог нажатием кнопки **Start**. Затем отправьте команду ```/newbot``` и укажите параметры нового бота:
- **имя** (на любом языке), под которым ваш бот будет отображаться в списке контактов;е
- **техническое имя вашего бота** по которому его можно будет найти в Telegram. Имя должно оканчиваться на слово bot в любом регистре

Аккаунт вашего бота создан. **BotFather** поздравит вас и отправит в чат токен для работы с Bot API. Токен выглядит примерно так: ```123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11```

Получите свой токен от **Яндекс Практикума** по адресу *https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a* 

## Заселяем бота на сервер
```Примечание: дальнейшии инструкции составлены на основе работы с сервером на OS Ubuntu 20.04. Однако алгоритм действий запуска проекта на локальной машине аналогичен.```

Клонируйте данный репозиторий в рабочую директорию на сервере и перейдите в нее:
```
git clone git@github.com:Belyanski/homework_bot.git
```
```
cd homework_bot/
```
Cоздайте и активируйте виртуальное окружение:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
Установите зависимости проекта:
```
pip install -r requirements.txt
``` 
В корневой директории проекта создайте файл для секретов:
```
nano .env
```
Вы окажетесь в редакторе **nano**, где вам необходимо прописать токен, полученный от **BotFather**, ваш токен от **Яндекс Практикума** и  id профиля от аккаунта в **Telegram**: 
```
TELEGRAM_TOKEN=
PRACTICUM_TOKEN=
TELEGRAM_CHAT_ID=
```
Затем нажмите ```Ctrl+X```, согласитесь с сохранением изменений ```Y``` и подтвердите название файла ```Enter```

Запустите бота:
```
python homework.py
```
## Режим демона

Сперва нужно создать юнита для системного демона ```systemd```:
```
sudo nano /etc/systemd/system/homework_bot.service # Для юнита допустимо любое другое название
```
Запишите следующий код из листинга:
```
[Unit]
Description=Homework bot
After=syslog.target
After=network.target

[Service]
Type=simple
User=root  # Необходимо заменить на имя пользователя вашего сервера
WorkingDirectory=/root/homework_bot
ExecStart=/root/homework_bot/venv/bin/python /root/homework_bot/homework.py  # Путь до Python и исполняемого файла
RestartSec=10
Restart=always
 
[Install]
WantedBy=multi-user.target
```
Затем нажмите ```Ctrl+X```, согласитесь с сохранением изменений ```Y``` и подтвердите название файла ```Enter```.

Далее введите последовательно следующие команды: 

```
systemctl daemon-reload
systemctl enable homework_bot
systemctl start homework_bot
systemctl status homework_bot
```
Теперь бот работает в фоновом режиме и всегда с вами!


#### Автор проекта
[Ярослав Белянский](https://github.com/Belyanski)
