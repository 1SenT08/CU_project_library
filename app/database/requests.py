from sqlalchemy import select

from app.database.create_tables import User, Admin, File_library_kgu, async_session
from colorama import Fore, init, Style


init(autoreset=True)


async def post_user(user_id) -> None:
    async with async_session() as session:

        if user_id not in [user.tg_id for user in await session.execute(select(User.tg_id))]:
            user = User(tg_id=user_id)
            session.add(user)
            await session.commit()


async def post_admin(admin_id, name_admin) -> bool:
    async with async_session() as session:
        if admin_id not in [str(admin.tg_id) for admin in await session.execute(select(Admin.tg_id))]:
            if admin_id.isdigit():
                admin = Admin(tg_id=int(admin_id), name_admin=name_admin)
                session.add(admin)
                await session.commit()
                return True
        return False


async def post_file_v2(file_path, tg_id_file, name_file_on_disk, name_file,
                       autor, name_book, main_words, availability_photo,
                       photo_words) -> bool:
    
    async with async_session() as session:
        file = File_library_kgu(file_path=file_path, tg_id_file=tg_id_file, name_file_on_disk=name_file_on_disk,
                     name_file=name_file, autor=autor, name_book=name_book, main_words=main_words,
                     availability_photo=availability_photo, photo_words=photo_words)
        
        session.add(file)
        await session.commit()
        return True


async def get_name_files():
    async with async_session() as session:
        return_name_list_files = await session.execute(select(File_library_kgu.name_file))
        return return_name_list_files.scalars().all()


async def get_id_files():
    async with async_session() as session:
        return_id_list_files = await session.execute(select(File_library_kgu.id))
        return return_id_list_files.scalars().all()


async def get_files_by_id(list_id: list) -> list:
    async with async_session() as session:
        return_list_files = await session.scalars(select(File_library_kgu).where(File_library_kgu.id.in_(list_id)))
        return sorted([row.__dict__ for row in return_list_files.all()],
                      key=lambda x: list_id.index(x['id']))


async def get_particular_files_v2(particular_values: dict):
    async with async_session() as session:

        return_list_files = await session.execute(select(File_library_kgu))
        return_list_files = return_list_files.scalars().all()

        if len(return_list_files) == 0:
            print(Style.BRIGHT + 'Файлов в БД не существует' + Fore.RED)
            return []

        print(Style.BRIGHT + f"Выгрузка файлов из requests.py-get_particular_files_v2 в search_algorithm-func_searching_files_v2  прошла успешна" + Fore.GREEN)

        return [row.__dict__ for row in return_list_files]

        # print([row.__dict__ for row in return_list_admins.scalars().all()])
        # return return_list_admins.scalars().all(


async def get_admins():
    async with async_session() as session:
        # return_list_admins = await session.scalars(select(Admin).where(Admin.tg_id.in_([1000274111, 12312312321])))
        # return return_list_admins.all()
        return_list_admins = await session.execute(select(Admin.tg_id))
        return return_list_admins.scalars().all()
        # return [row.__dict__ for row in return_list_admins.scalars().all()]


async def delete_admin(admin_id):
    async with async_session() as session:
        if admin_id in [user.tg_id for user in await session.execute(select(Admin.tg_id))]:
            await session.execute(Admin.__table__.delete().where(Admin.tg_id == admin_id))
            await session.commit()
            return True

        await session.commit()
        return False


async def delete_file_on_bd(file_name):
    async with async_session() as session:

        if file_name in [file.name_file for file in await session.execute(select(File_library_kgu.name_file))]:
            await session.execute(File_library_kgu.__table__.delete().where(File_library_kgu.name_file == file_name))
            await session.commit()

            print(f"Файл {file_name} был успешно удален из БД")
            return True

        await session.commit()
        print(f"Такого названия файла не существует в БД")
        return False


async def amount_files():
    async with async_session() as session:
        return len([file for file in await session.execute(select(File_library_kgu))])

