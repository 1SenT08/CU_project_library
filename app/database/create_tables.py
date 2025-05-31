from sqlalchemy import String
from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from config import SQLALCHEMY_URL


engine = create_async_engine(SQLALCHEMY_URL, echo=True)
async_session = async_sessionmaker(engine)
          

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

    def __repr__(self):
        return f"User(id={self.id!r}, tg_id={self.tg_id!r})"


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

    name_admin: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"Admin(id={self.id!r}, tg_id={self.tg_id!r}, name_admin={self.name_admin!r})"


class File_library_kgu(Base):
    __tablename__ = "file_library_kgu"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_path = mapped_column(String) # 20
    tg_id_file = mapped_column(String) # 20
    name_file_on_disk = mapped_column(String) # 50

    name_file = mapped_column(String)
    autor = mapped_column(String)
    name_book = mapped_column(String)
    main_words = mapped_column(String)
    availability_photo = mapped_column(String)
    photo_words = mapped_column(String)

    def __repr__(self):
        return f"File(id={self.id!r}, file_path={self.file_path!r},\
                tg_id_file={self.tg_id_file!r}, name_file_on_disk={self.name_file_on_disk!r},\
                name_file={self.name_file!r}, autor={self.autor!r},\
                name_book={self.name_book!r}, main_words={self.main_words!r},\
                availability_photo={self.availability_photo!r}, photo_words={self.photo_words!r})"


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

