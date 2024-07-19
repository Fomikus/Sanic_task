## ⚙ [Настройка](https://github.com/Fomikus/Sanic_task/blob/main/.env-example)
| Настройка                | Описание                                                               |
|--------------------------|------------------------------------------------------------------------|
| **POSTGRES_USER**        | Имя пользователя postgres _(напр. user_postgres)_                      |
| **POSTGRES_PASSWORD**    | Пароль пользователя postgres  _(напр. user_password)_                  |
| **POSTGRES_DB**          | Используемая база данных _(напр. user_database)_                       |
| **POSTGRES_HOST**        | HOST базы данных  _(напр. postgres_db)_                                |
| **SANIC_DEBUG**          | DEBUG Sanic _(True / False)_                                           |
| **SANIC_HOST**           | Хост для Sanic _(напр. 0.0.0.0)_                                       |
| **SANIC_JWT_SECRET_KEY** | Секретный ключ генерации JWT токенов _(напр. gfdmhghif38yrf9ew0jkf32)_ |

## 🧱 Установка
1. Клонирование репозитория
```shell
git clone https://github.com/Fomikus/Sanic_task.git
cd Sanic_task
```
2. Следуйте одной из инструкций ниже

## ⚡ Запуск Sanic приложения без Docker
0. 🧱 Для работы требуется активный сервер postgres. Данные для авторизации должны быть указаны в .env файле!
1. Запустите `install_local.bat` или `install_local.sh` в зависимости от системы для создания виртуального окружения и установки зависимостей.
2. Для запуска приложения используйте `start_local.bat` или `start_local.sh` в зависимости от системы.

## ⚡ Запуск контейнера с postgres/nginx/Sanic приложением
0. Создайте файл `.env` с настройками (Референс `.env-example`)
1. Выполните `docker-compose up` для создания контейнера вместе с postgres и nginx

## ⚡ Запуск с помощью Dockerfile
1. Выполните `docker build --tag sanic_task .`
2. Выполните `docker run --detach sanic_task`


## ⛓️ Тестирование
Для удобного тестирования импортируйте файл `SanicTask.postman_collection.json` в [Postman](https://postman.com)


## 🧪 Тестовые данные для авторизации
| Роль                | Email           | Пароль   |
|---------------------|-----------------|----------|
| **Пользователь**    | user@test.test  | password |
| **Администратор**   | admin@test.test | password |
