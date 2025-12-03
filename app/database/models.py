from dotenv import load_dotenv
import os
#логгер
from logger.logger_configuration import setup_logging
#sqlalchemy
from sqlalchemy import ForeignKey, BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, validates
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
from typing import Optional
load_dotenv()

logger = setup_logging()

engine = create_async_engine(os.getenv('DB_URL'), echo=False,pool_size=10)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    ...
    
class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    user_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,nullable= True)
    balance : Mapped[int] = mapped_column(String(20), nullable=True, default='0')
    
    @validates('tg_id')
    def validate_tg_id(self, key, tg_id):# key - имя атрибута, tg_id - его значение
        if not isinstance(tg_id, int):
            raise TypeError("tg_id must be integer")
        if tg_id < 0:
            raise ValueError("tg_id must be above 0")
        return tg_id
    @validates('user_name')
    def validate_username(self, key, user_name):# key - имя атрибута, tg_id - его значение
        if not isinstance(user_name, str):
            raise TypeError("user_name must be str")
        if len(user_name) < 0:
            raise ValueError("Имя больше нуля должно быть")
        return user_name
    
class AI_type(Base):
    '''Тип модели для опред запросов(текстовый, аудио, видео, фото)'''
    __tablename__ = "ai_types"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), unique=True)
    
class AI_Model(Base):
    '''Модель ai, связанная с AI_type'''
    __tablename__ = 'ai_models'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    ai_type: Mapped[int] = mapped_column(ForeignKey('ai_types.id'))
    price: Mapped[str] = mapped_column(String(20), nullable=True, default='0.1')
    
class Order(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(50))
    user: Mapped[int] = mapped_column(ForeignKey('users.id'))
    amount: Mapped[str] = mapped_column(String(15), default='0')
    created_at: Mapped[datetime] 
    order: Mapped[str] = mapped_column(String(100)) # уникальный номе заказа для ориентира
    
    
    
    
    
     
async def async_db_main():
    logger.info("Запусе дивжка для СУБД postgre")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
