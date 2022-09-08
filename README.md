![example workflow](https://github.com/JediMode/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Foodgram 

Проект Foodgram реализован для обмена рецептами. Авторизованные пользователи
могут публиковать свои рецепты, подписываться на понравившихся авторов, добавлять рецепты в избранное,
составлять список покупок и скачивать его себе в формате pdf.

## Описание Workflow
### Workflow состоит из четырёх шагов:
#### tests
- Проверка кода на соответствие PEP8.
#### push Docker image to Docker Hub
- Сборка и публикация образа на DockerHub.
#### deploy 
- Автоматический деплой на боевой сервер при пуше в главную ветку.
#### send_massage
- Отправка уведомления в телеграм-чат.

## Подготовка и запуск проекта
### Склонировать репозиторий на локальную машину:
```
git clone https://github.com/JediMode/foodgram-project-react
```
## Для работы с удаленным сервером (на ubuntu):
* Выполните вход на свой удаленный сервер

* Установите docker на сервер:
```
sudo apt install docker.io 
```
* Установите docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
* Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
* Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```

* Cоздайте .env файл и впишите:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ проекта django>
    ```
* Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
    ```
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    
    SECRET_KEY=<секретный ключ проекта django>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
  
* На сервере соберите docker-compose:
```
sudo docker-compose up -d --build
```
* После успешной сборки на сервере выполните команды (только после первого деплоя):
    - Соберите статические файлы:
    ```
    sudo docker-compose exec web python manage.py collectstatic --noinput
    ```
    - Примените миграции:
    ```
    sudo docker-compose exec web python manage.py migrate --noinput
    ```
    - Загрузите ингридиенты  в базу данных:  
    ```
    sudo docker-compose exec web python manage.py load_data
    ```
    - Создать суперпользователя Django:
    ```
    sudo docker-compose exec web python manage.py createsuperuser
    ```
    - Проект будет доступен по вашему IP

## Проект в интернете
Проект запущен и доступен по адресу (http://158.160.7.15/recipes)
