import logging
import os
import sys
import time

import requests
import telegram
from typing import Union

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения нужных для работы."""
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def send_message(bot: telegram.Bot, message: str) -> None:
    """отправляет сообщение в Telegram чат."""
    try:
        logging.debug(f'Бот отправил сообщение {message}')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(error)


def get_api_answer(current_timestamp: int) -> Union[dict, str]:
    """создает и отправляет запрос к эндпоинту."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
        code = homework_statuses.status_code
        if code == 200:
            homework_statuses = homework_statuses.json()
            return homework_statuses
        else:
            raise Exception(f'эндпоинт {ENDPOINT} недоступен. '
                            f'Код ответа API: {code}')
    except Exception:
        raise Exception('прочие ошибки при запросе к эндпойту')


def check_response(response: dict) -> list:
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError(f'Ответ API возвращает {type(response)} вместо dict')
    if response.get('current_date') is None:
        raise KeyError('В ответе API отсутствует ключ current_date')
    homeworks = response.get('homeworks')
    if homeworks is None:
        raise KeyError('В ответе API отсутствует ключ homework')
    if not isinstance(homeworks, list):
        raise TypeError(
            f'В ответе API homework является {type(homeworks)} вместо list'
        )
    return homeworks


def parse_status(homework: dict) -> str:
    """Извлекает статус конкретной домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        raise KeyError('В ответе API отсутствует ключ homework_name')
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(f'Статус {homework_status} не найден')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    last_send = {
        'error': None,
    }
    if not check_tokens():
        logging.critical(
            'Отсутствует обязательная переменная окружения.\n'
            'Программа принудительно остановлена.'
        )
        exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if len(homeworks) == 0:
                logging.debug('Ответ API пуст: нет домашних работ.')
                break
            for homework in homeworks:
                message = parse_status(homework)
                if last_send.get(homework['homework_name']) != message:
                    send_message(bot, message)
                    last_send[homework['homework_name']] = message
            current_timestamp = response.get('current_date')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if last_send['error'] != message:
                send_message(bot, message)
                last_send['error'] = message
        else:
            last_send['error'] = None
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        stream=sys.stdout
    )
    main()
