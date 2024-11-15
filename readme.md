API иммитирующей торговую платформу(брокерское приложение - backend)


- Аутентификация пользователей с помощью токенов JWT
- Регистрация пользователей и управление профилем 
- Система персональных кошельков
- Отслеживание цен на активы в режиме реального времени через http запросы к Binance (без использования библиотеки для работы с Binance API)
- Торговые операции (покупка, продажа, шорт, закрытие шорта)
- Кэширование Redis для повышения производительности

## Тех.требования
- python 3.8+
- FastAPI latest
- SQLAlchemy latest
- Redis latest
- Pydantic latest
- JWT Authentication (Jose)

## API Ручки (Эндпоинты)

### Аутентификация и пользователи
| Метод | Endpoint | Описание | Тело запроса | Ответ |
|-------|----------|----------|--------------|-------|
| POST | `/login` | Аутентификация пользователя | ```json { "username": "string", "password": "string" }``` | ```json { "access_token": "string", "token_type": "bearer" }``` |
| POST | `/new_user` | Создание нового пользователя | ```json { "username": "string", "email": "string", "password": "string" }``` | Возвращает объект созданного пользователя |
| GET | `/get_user_by_id` | Получение информации о пользователе | Query параметр: `user_id` | Возвращает объект пользователя |

### Управление кошельком
| Метод | Endpoint | Описание | Требования | Ответ |
|-------|----------|----------|------------|-------|
| GET | `/get_user_wallet_by_user_id` | Получение информации о кошельке пользователя | JWT Token | Возвращает объект кошелька |

### Торговые операции
| Метод | Endpoint | Описание | Параметры | Ответ |
|-------|----------|----------|-----------|-------|
| GET | `/asset_data` | Получение текущей цены актива | Query параметр: `asset_name` | Возвращает данные о цене |
| POST | `/transaction` | Выполнение торговой операции | ```json { "asset_name": "string", "amount": integer, "transaction_type": "buy/sell/short/close_short" }``` | ```json { "status": "success" }``` |


### Аутентификация

Все эндпоинты, кроме `/login` и `/new_user`, требуют JWT-аутентификации. 
Токен необходимо передавать в заголовке:
```
Authorization: Bearer <JWT-токен>
```

Реализована валидация данных с помощью Pydantic.
Используется хранение данных в Redis.
Установлена жесткая изоляция транзакций (isolation level: SERIALIZABLE)



