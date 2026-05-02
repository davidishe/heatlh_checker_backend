# heatlh_checker_backend

Минимальный Python health-checker backend.

## Эндпоинты
- `GET /health`
- `GET /health/deep`

## Локальный запуск
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

По умолчанию сервис стартует на `0.0.0.0:8000`.
