![foodgram](https://github.com/kolian338/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
# Foodgram - «Продуктовый помощник»
## Описание проекта
Cервис, где пользователи могут публиковать рецепты, подписываться на 
публикации других пользователей, добавлять понравившиеся рецепты в 
список «Избранное», скачивать сводный список продуктов, необходимых для
приготовления одного или нескольких выбранных блюд.

## Ссылка на веб-приложение и документацию
[Страница входа](http://158.160.72.142/signin)

[Документация](http://158.160.72.142/api/docs/redoc.html)

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
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<секретный ключ проекта django>
ALLOWED_HOSTS=<рашрешенные адреса>
```
Так же необходимо задать секреты в gihub actions:
```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>

DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>

SECRET_KEY=<секретный ключ проекта django>
ALLOWED_HOSTS=<рашрешенные адреса>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```
Запустить docker-compose.yml:
```
Перед запуском:
- На сервере создать папку food_gram и перенести в неё docker-compose.yml
- И перенести nginx.conf

docker compose -f docker-compose.yml up
```

Создать суперпользователя:
```
docker exec -it infra_web_1 python manage.py createsuperuser
```
Чтобы заполнить базу данных начальными данными списка ингридиетов выполните:
```
sudo docker exec infra_web_1 python manage.py import_csv_command --path recipes/management/commands/data/ingredients.csv
```

При локальном запуске в settings можно использовать БД sqlite:
```
- В settings добавить:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

Выполнить команды:
- python manage.py makemigrations
- python manage.py migrate
```