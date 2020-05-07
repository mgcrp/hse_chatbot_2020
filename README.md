# hse_chatbot_2020
## Курсовой проект "Чат бот рекомендует"

### Команда проекта:
* Кудрявцева Софья
* Никифоров Алексей
* Попов Илья

### Логические этапы проекта:

1. Данные о предпочтениях пользователей
  * Форма для прохождения опроса - https://forms.gle/DDhVYwSGFefYT6ke8
  * Гуглодок с данными из формы -  https://docs.google.com/spreadsheets/d/1_DZeuWzxIIpELsrBTOqzYJ4WYNqROMs2v40WyyrqGwg
  
2. Модель
  * Тут будет описание модели 1
  * Тут будет описание модели 2
  
3. Данные от Яндекс.Маркет
  * Список категорий + метод их получения
  * Функция для получения топ товаров в категории
  * Функция для получения информации о товаре в категории
  
4. Бот
  * Сбор данных от пользователя
  * Вызов функции с predict'ом от модели
  * Логирование информации о запросе для дальшейшей аналитики
  
5. Инфраструктура
  * Хостинг на Google Cloud Services
  * Организация хранения данных на PostgeSQL
  * Организация сценария для повторного обучения модели
    * Либо вызов от бота при определенном сценарии (после n новых запросов)
    * Либо скриптованый вызов по времени (crontabs на сервере)
    
### TODO:

* Тут будет описание модели 1 (Соня/Лёша)
* Тут будет описание модели 2 (Соня/Лёша)
* Функция predict для бота (Соня/Лёша)
  * Принимает данные в стандартном виде, грузит модель из файла, возвращает одну или несколько категорий Яндекс.Маркет
* Функция learn для бота (Соня/Лёша)
  * Принимает датафрейм в стандартном виде, обучает модель с заданными заранее гиперпараметрами и сохраняет новую модель в файл
* Вывод результата ботом (Илья)
* Заезд бота на хостинг (Илья)
* Организация хранения данных в PostgreSQL на сервере (Илья)
* Переезд бота с pooling запросов на webhook (Илья)
