-- init.sql
-- Создание таблицы пользователей, если она не существует
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,  -- Уникальный идентификатор пользователя
    email VARCHAR(255) UNIQUE NOT NULL,  -- Уникальный email пользователя
    password_hash VARCHAR(255) NOT NULL  -- Хэшированный пароль пользователя
);

-- Создание таблицы истории входов, если она не существует
CREATE TABLE IF NOT EXISTS login_history (
    id SERIAL PRIMARY KEY,  -- Уникальный идентификатор записи
    user_id INTEGER REFERENCES users(id),  -- Внешний ключ на таблицу users
    user_agent TEXT,  -- Информация о браузере или устройстве пользователя
    login_time TIMESTAMP  -- Время входа пользователя
);