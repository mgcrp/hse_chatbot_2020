# hse_chatbot_2020

<img src="logo.png" width="100" height="100">

## Курсовой проект "Чат бот рекомендует"

### Команда проекта:
* Кудрявцева Софья
* Никифоров Алексей
* Попов Илья

**[Отчет](docs/Отчет_Чат_бот_Кудрявцева_Никифоров_Попов.pdf) о выполнении курсовой работы**

### Логические этапы проекта:

1. Данные о предпочтениях пользователей
  * [Форма](https://forms.gle/DDhVYwSGFefYT6ke8) для прохождения опроса
  * [Гуглодок](https://docs.google.com/spreadsheets/d/1_DZeuWzxIIpELsrBTOqzYJ4WYNqROMs2v40WyyrqGwg) с данными из формы
  ---
  * [Файл](data/categories_with_yandex.csv) с категориями Яндекс.Маркет
  * [Файл](data/training_sample.csv) с полной обучающей выборкой
  * [Файл](data/training_sample_unique.csv) с обучающей выборкой, обобщенной до уникальных профилей
  * [Файл](data/training_sample_xgboost.csv) с обучающей выборкой для модели XGBoost
  
2. Модель
  * [Jupyter Notebook](experiments/models.ipynb) с экспериментами над моделями
  * [baseline](model/baseline.py) - Базовый вариант модели - Используется RandomForest
  * [model1](model/model1.py) - Доработанная модель на основе RandomForest
  * [model2](model/model2.py) - Модель на основе нейронной сети
  * [model3](model/model3.py) - Модель на основе KNN
  * [model4](model/model4.py) - Модель на основе XGBoost
  
3. Данные от Яндекс.Маркет
  * [Jupyter Notebook](experiments/yandex_experiments.ipynb) со всеми экспериментами с API Яндекс.Маркет
  * [product.py](model/product.py)
    * **getTopInCategory** - Возвращает `n` первых по популярности товаров в категории `category_id` заданым ограничением по цене (сортировка по популярности на Яндекс.Маркет)
  * [market_utils.py](bot/market_utils.py)
    * **getDataByYandexID** - Возвращает информацию о товаре по введенному ID модели
  * [Файл](data/categories_with_yandex.csv) с категориями Яндекс.Маркет
  
4. Бот
  * [bot.py](bot/bot.py) - Главный файл бота
  * [localization.py](bot/localization.py) - Файл с локализацией - Содержит весь текст, который бот отправляет пользователю. Такая структура позволяет легко и быстро осуществить перевод интерфейса на другой язык и подключить его без танцев с бубном
  * [market_utils.py](bot/market_util.py) - Набор функций для взаимодействия с API Яндекс.Маркет
  * [model_utils.py](bot/model_utils.py) - Набор функций для взаимодействия с моделью
  * [sql_utils.py](bot/sql_utils.py) - Набор функций для взаимодействия с СУБД PostgreSQL
  
5. Инфраструктура
  * [Скрипт](sql/create.sql) для создания БД в СУБД PostgreSQL
---
  * Хостинг на Google Cloud Services
  * Организация хранения данных на PostgeSQL
  * Организация сценария для повторного обучения модели
    * Либо вызов от бота при определенном сценарии (после n новых запросов)
    * Либо скриптованый вызов по времени (crontabs на сервере)
    
### TODO:

* Заезд бота на хостинг
* Организация хранения данных в PostgreSQL на сервере
* Переезд бота с pooling запросов на webhook
