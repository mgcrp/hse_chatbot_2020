-- Создание БД
DROP DATABASE IF EXISTS chatbot;
CREATE DATABASE chatbot;

\connect chatbot

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

-- Создание схемы
CREATE SCHEMA dbo;
COMMENT ON SCHEMA public IS 'project default schema';
SET search_path = dbo;

-- Таблица user_reactions
CREATE TABLE chatbot.dbo.user_reactions (
    ID                      INT                     GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    modifyDate              TIMESTAMP               DEFAULT now(),
    telegram_id             NUMERIC                 NOT NULL,
    telegram_username       TEXT                    NOT NULL,
    telegram_first_name     TEXT,
    telegram_last_name      TEXT,
    telegram_language_code  TEXT,
    recipient_sex           TEXT                    NOT NULL,
    recipient_age           INT                     NOT NULL,
    recipient_status        TEXT                    NOT NULL,
    recipient_hobby         TEXT[]                  NOT NULL,
    recipient_max_cost      INT                     NOT NULL,
    recipient_reason        TEXT                    NOT NULL,
    suggestion_model_id     NUMERIC                 NOT NULL,
    suggestion_category_id  NUMERIC                 NOT NULL,
    user_reaction           TEXT
);

-- Create user
CREATE USER chatbot_user WITH ENCRYPTED PASSWORD 'chatbot_password' SUPERUSER;

-- Delete user
REASSIGN OWNED BY chatbot_user TO postgres;
DROP OWNED BY chatbot_user;
DROP USER chatbot_user;

-- Select example
select * from chatbot.dbo.user_reactions limit 10;