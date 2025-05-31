from app.database.requests import get_particular_files_v2
from app.filter import pretext


async def func_searching_files_v2(requirements: dict):
    return_list_files = []
    max_amount_values = 50
    request_files = await get_particular_files_v2(requirements)


    if len(request_files) > 0:
        dispointment_dict = {
                "name_file": 5,
                "autor": 2,
                "name_book": 3,
                "availability_photo": 0.5
            }

        for file in request_files:
            file['probability'] = 0
            
            # Faze 1:
            for key in dispointment_dict:
                if file[key].lower().strip() == requirements[key].lower().strip():
                    file['probability'] += dispointment_dict[key]

            # Faze 2:
            for key in ["name_file", "autor", "name_book",
                        "main_words", "photo_words"]:
                if requirements[key] == "-" or file[key] == "-":
                    continue

                if key == "name_file" and file["name_file_on_disk"] != "-":
                    continue
    
                for word_key in file[key].split("_"):
                    if word_key.strip().lower() in requirements[key].strip().lower() and pretext(word_key.strip().lower()):
                        file['probability'] += 1
                        print(word_key.strip().lower(), requirements[key].strip().lower())

                for word_key in requirements[key].split("_"):
                    if word_key.strip().lower() in file[key].strip().lower() and pretext(word_key.strip().lower()):
                        file['probability'] += 1
                        print(word_key.strip().lower(), requirements[key].strip().lower())
            
            # Faze for file on disk
            if file["name_file_on_disk"] != "-":
                for word_key in file["name_file"].lower().split():
                    if word_key.strip() in requirements["name_file"].strip().lower() and pretext(word_key.strip().lower()):
                        file['probability'] += 1

                for word_key in requirements["name_file"].lower().split("_"):
                    if word_key.strip() in file["name_file"].strip().lower() and pretext(word_key.strip().lower()):
                        file['probability'] += 1


            if file["probability"] > 1 and len(return_list_files) <= 5:
                return_list_files.append(file)

            elif file["probability"] > 2 and len(return_list_files) <= 10:
                return_list_files.append(file)
            
            elif file["probability"] > 3 and len(return_list_files) <= 15:
                return_list_files.append(file)
            
            elif file["probability"] > 5:
                return_list_files.append(file)

        if len(return_list_files) <= max_amount_values:
            print(f"Поиск нужных файлов прошел успешно")
            print(len(return_list_files), return_list_files)
            return ([str(file["id"]) for file in sorted(return_list_files, key=lambda x: x['probability'], reverse=True)],
                    True)

        else:
            print(f"Поиск нужных файлов прошел успешно")
            return ([str(file["id"]) for file in sorted(return_list_files, key=lambda x: x['probability'],
                                                   reverse=True)[:max_amount_values]], True)

    else:
        print(f"Нужных файлов не удалось найти")
        return [], False

