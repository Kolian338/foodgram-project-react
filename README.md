![foodgram](https://github.com/kolian338/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
# Foodgram - «Продуктовый помощник»
## Описание проекта
Cервис, где пользователи могут публиковать рецепты, подписываться на 
публикации других пользователей, добавлять понравившиеся рецепты в 
список «Избранное», скачивать сводный список продуктов, необходимых для
приготовления одного или нескольких выбранных блюд.

## Ссылка на веб-приложение и документацию
http://158.160.72.142/signin
<br>
http://158.160.72.142/api/docs/redoc.html

## Технологии
* Python 3.9
* Django==3.2.3
* djangorestframework==3.12.4 
* nginx
* gunicorn==20.1.0
* djoser==2.1.0
* PostgreSQL
* Docker
* React

## Автор
Nikolay Safonov

## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
gti clone git@github.com:Kolian338/foodgram-project-react.git
```

Создать файл .evn для хранения ключей, в папке infra:

```python
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432

Так жя необходимо задать секреты в gihub actions:
ALLOWED_HOSTS=localhost 127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DOCKER_PASSWORD=passwod
DOCKER_USERNAME=kolian338
HOST=158.160.72.142
PASSPHRASE=server_password
SSH_KEY=ssh_key
USER=server_name
TELEGRAM_TO=account_id
TELEGRAM_TOKEN=bot_token



```
Запустить docker-compose.yml:
```
Перед запуском:
- На сервере создать папку food_gram и перенести в неё docker-compose.yml
- И перенести nginx.conf

docker compose -f docker-compose.yml up
При локальном запуске в settings можно использовать БД sqlite
```
Создать суперпользователя:
```
docker exec -it infra_web_1 python manage.py createsuperuser
```
Чтобы заполнить базу данных начальными данными списка ингридиетов выполните:
```python
sudo docker exec infra_web_1 python manage.py import_csv_command --path recipes/management/commands/data/ingredients.csv
```