# heatlh_checker_backend

Backend-сервис health checker с HTTP health-эндпоинтами и отдельным планировщиком проверок URL.

## Что делает проект

1. Flask-приложение поднимает API:
   - `GET /health`
   - `GET /health/deep`
2. Отдельный скрипт `checker.py` читает `urls.txt` и проверяет каждый URL.
3. Скрипт запускается по расписанию **каждые 5 минут** через `systemd timer` (создаётся в deploy workflow).
4. Если URL вернул timeout / 5xx / ошибку запроса — отправляется уведомление в Telegram.

## Откуда берутся URL

По умолчанию используется файл `urls.txt` в корне репозитория.

- Можно переопределить через env: `URLS_FILE=/abs/path/or/relative/path`.
- Формат файла: один URL в строке.
- Пустые строки и строки, начинающиеся с `#`, игнорируются.

Пример:

```txt
https://example.com/health
https://api.example.com/ping
# https://temporary-disabled-service.local/health
```

## Переменные окружения

Обязательные для Telegram-уведомлений:

- `TELEGRAM_BOT_TOKEN` — токен Telegram бота
- `CHAT_ID` — chat id, куда отправлять алерты

Дополнительно:

- `CHECK_TIMEOUT` — timeout HTTP-проверки в секундах (по умолчанию `10`)
- `URLS_FILE` — путь к файлу со списком URL (по умолчанию `urls.txt`)
- `PORT` — порт Flask-приложения (по умолчанию `8000`)

## Логи и статусы

`checker.py` пишет логи в stdout (они попадают в `journalctl` через systemd):

- Старт прогона:
  - `[INFO] <iso-ts> run_started urls_count=<n> urls_file=<path>`
- Успешная проверка URL:
  - `[OK] <iso-ts> url=<url> status=http_<code>`
- Ошибка проверки URL:
  - `[FAIL] <iso-ts> url=<url> status=timeout|http_5xx|error=...`
- Отправка Telegram:
  - `[ALERT] <iso-ts> telegram_send status=<http> ok=<true|false>`
- Завершение:
  - `[INFO] <iso-ts> run_finished failed=<n> total=<n>`

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Однократная ручная проверка URL:

```bash
source .venv/bin/activate
export TELEGRAM_BOT_TOKEN=...
export CHAT_ID=...
python checker.py
```

## Деплой и расписание

GitHub Actions workflow `.github/workflows/deploy.yml` при пуше в `main`:

1. обновляет код в `/var/apps/backend/heatlh_checker_backend`;
2. создает/обновляет `.env` (подставляет `TELEGRAM_BOT_TOKEN` и `CHAT_ID` из GitHub Secrets);
3. ставит зависимости Python;
4. создает systemd unit-файлы:
   - `heatlh-checker-run.service` — единичный запуск `checker.py`
   - `heatlh-checker-run.timer` — запуск каждые 5 минут (`OnCalendar=*:0/5`)
5. включает и перезапускает timer.

## Какие GitHub Secrets нужны

- `DEPLOY_SSH_HOST`
- `DEPLOY_SSH_USER`
- `DEPLOY_SSH_KEY`
- `DEPLOY_SSH_PORT`
- `TELEGRAM_BOT_TOKEN`
- `CHAT_ID`

