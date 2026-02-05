# Booking API

REST API для бронирования переговорных. Django + DRF, авторизация через JWT, Postgres в Docker.

## Что умеет

- регистрация и логин (JWT)
- публичный список комнат
- создание и отмена своих бронирований
- админ управляет комнатами и видит все брони
- на одной комнате нельзя пересечь активные интервалы

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

Если `8000` занят:

```bash
WEB_PORT=18000 docker compose up --build
```

После старта:

- docs: `http://127.0.0.1:8000/api/docs/`
- admin: `http://127.0.0.1:8000/admin/`

Суперпользователь:

```bash
docker compose exec web python manage.py createsuperuser
```

Локально без Docker (sqlite, если не задан `POSTGRES_HOST`):

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Основные ручки

| Метод | URL | Доступ |
|-------|-----|--------|
| POST | `/api/auth/register/` | все |
| POST | `/api/auth/token/` | все |
| POST | `/api/auth/token/refresh/` | все |
| GET/PATCH | `/api/users/me/` | авторизованные |
| GET | `/api/rooms/` | все |
| POST/PUT/PATCH/DELETE | `/api/rooms/` | админ |
| GET/POST | `/api/bookings/` | авторизованные |
| POST | `/api/bookings/{id}/cancel/` | владелец / админ |

Для запросов с JWT:

```text
Authorization: Bearer <access_token>
```

## Тесты

```bash
POSTGRES_HOST= python manage.py test
```

## Структура

- `users` — пользователь, регистрация, профиль
- `bookings` — комнаты и бронирования
- `config` — настройки и корневые урлы
