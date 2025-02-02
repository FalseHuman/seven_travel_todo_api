# Бекенд-система To-Do List (тестовое задание)

Бекенд-система To-Do List, это система которая позволяет людям фиксировать свои задачи
### Функционал
- Регистрация пользователя
- CRUD задач

### Интересное
- Аутентификация пользователя с использованием JWT
- Тесты

### Инструменты

- Python >= 3.9
- FastAPI
- Postgres

## Старт

#### 1) В корне проекта создать .env и прописать свои настройки
    SECRET_KEY=Ключ_для_шифрования_паролей # Для проверки тестового задания можно использовать это ключ f8abdb348db1b51998d134fdba20c7b179ac416938eb72f22370f4278fc05b6d
    ALGORITHM=Алгоритм_шифрования # Для проверки тестового задания можно использовать данный алгоритм HS256


#### 2) Создать образ и запустить контейнер (dev)

    docker compose -f docker-compose.dev.yml up -d --build 
    
#### 2.1) Создать образ и запустить контейнер (prod)

    docker compose -f docker-compose.prod.yml up -d --build   
    
##### 3) Выполнить миграции(dev)

     docker compose -f docker-compose.dev.yml exec web alembic upgrade head 

##### 3.1) Выполнить миграции(prod)

     docker compose -f docker-compose.prod.yml exec web alembic upgrade head 


##### 4) Перейти по адресу

    http://localhost:8000/docs 
    
##### 5) Запуск тестов
```
docker compose -f docker-compose.dev.yml exec web alembic pytest
```

                                                        
##### 0) Если нужно очистить БД

    docker-compose down -v
    
## Примеры curl

#### 1) Создание пользователя
```
curl -X 'POST' \
  'http://localhost:8000/auth/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "string",
  "email": "string",
  "password": "string"
}'
```

#### 2) Получение токена
```
curl -X 'POST' \
  'http://localhost:8000/auth/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=string&password=string&scope=&client_id=&client_secret='
```
    
#### 3) Создание задачи
```
curl -X 'POST' \
  'http://localhost:8000/tasks/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <тут_JWT_token>' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "string",
  "description": "string",
  "status": "todo"
}'
```

#### 4) Фильтрация задач
```
curl -X 'GET' \
  'http://localhost:8000/tasks/?todo_status=todo' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <тут_JWT_token> '
```
    
    
    