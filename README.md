<h1 align="center">Foodgram</h1>

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
<h2 align="center">
  
  
</h2>

<h3 align="center">Описание</h3>

**Foodgram**  - веб-приложение для публикации рецептов. Авторизованные пользователи могут подписываться 
на понравившихся авторов, добавлять рецепты в избранное, ингредиенты понравившихся рецептов добавлять 
в список покупок, который можно выгрузить в текстовый файл.   

<h3 align="center">Как запустить проект</h3>

Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:elityaev/foodgram-project-react.git
cd foodgram-project-react
```
Cкопировать `.env.example` и назвать его `.env`, заполнить переменные окружения

Шаблон наполнения env-файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
```
Перейти в папку `backend`, установить зависимости из файла requirements.txt:

```
cd backend
pip install -r requirements.txt
```
Выполнить миграции:

```
python manage.py migrate
```
Заполнить таблицы `Tag` и `Ingredient`, выполнив команду:
```
python manage.py db_load
```
Запустить проект:

```
python3 manage.py runserver
```