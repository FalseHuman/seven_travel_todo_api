import pytest
import pytest_asyncio
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, create_engine
from sqlalchemy.future import select
from sqlalchemy import insert
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt

# Определение базовой модели
Base = declarative_base()

# Определение модели пользователя
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

# Определение модели задачи
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    status = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

# Временное создание базы данных
DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # Использование in-memory SQLite базы данных
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Создание приложения FastAPI
app = FastAPI()

async def get_db():
    async with SessionLocal() as session:
        yield session

# Библиотека для хэширования паролей
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
SECRET_KEY = "mysecretkey"  # Используйте свой секретный ключ
ALGORITHM = "HS256"

async def create_access_token(username: str, user_id: int, is_admin: bool, is_active: bool, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'is_admin': is_admin, 'is_active': is_active}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post('/auth/', status_code=201)
async def create_user(db: AsyncSession = Depends(get_db), username: str = "", email: str = "", password: str = ""):
    hashed_password = bcrypt_context.hash(password)
    await db.execute(insert(User).values(username=username, email=email, hashed_password=hashed_password))
    await db.commit()
    return {"status_code": 201, "transaction": "User created successfully"}

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@app.post('/auth/token')
async def login(db: AsyncSession = Depends(get_db), username: str = "", password: str = ""):
    user = await authenticate_user(db, username, password)
    token = await create_access_token(user.username, user.id, user.is_admin, user.is_active, expires_delta=timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}

@app.get('/tasks/', status_code=200)
async def all_tasks(db: AsyncSession = Depends(get_db), user_id: int = 1):
    tasks = await db.scalars(select(Task).where(Task.user_id == user_id))
    return tasks.all()

@app.post('/tasks/', status_code=201)
async def post_task(db: AsyncSession = Depends(get_db), title: str = "", description: str = "", status: str = "", user_id: int = 1):
    await db.execute(insert(Task).values(title=title, description=description, status=status, user_id=user_id))
    await db.commit()
    return {"status_code": 201, "transaction": "Task created successfully"}

# Тесты
@pytest_asyncio.fixture(scope="module")
async def test_app():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield TestClient(app)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_user(test_app):
    response = test_app.post("/auth/", json={"username": "testuser", "email": "test@example.com", "password": "testpass"})
    assert response.status_code == 201
    assert response.json() == {"status_code": 201, "transaction": "User created successfully"}

@pytest.mark.asyncio
async def test_login(test_app):
    response = test_app.post("/auth/token", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_create_task_as_authenticated_user(test_app):
    # Сначала создаем пользователя и получаем токен
    login_response = test_app.post("/auth/token", data={"username": "testuser", "password": "testpass"})
    token = login_response.json()["access_token"]

    # Создание задачи как авторизованный пользователь
    response = test_app.post("/tasks/", json={"title": "Test Task", "description": "Test Description", "status": "todo"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["transaction"] == "Task created successfully"

@pytest.mark.asyncio
async def test_get_user_tasks(test_app):
    login_response = test_app.post("/auth/token", data={"username": "testuser", "password": "testpass"})
    token = login_response.json()["access_token"]

    # Создадим задачу для получения задач пользователя
    test_app.post("/tasks/", json={"title": "Another Task", "description": "Some Description", "status": "todo"}, headers={"Authorization": f"Bearer {token}"})

    # Получение задач для пользователя
    response = test_app.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0  # Убедимся, что задачи возвращаются
