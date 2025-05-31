import requests


URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN_API = ""
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'OAuth {TOKEN_API}'
}


class File_disk:
    def __init__(self, url, bot_token):
        self.url = url
        self.bot_token = bot_token

    async def post_file(self, name_file, path_file):
        post = f"{self.url}/upload?path={name_file}.pdf&url=https://api.telegram.org/file/bot{self.bot_token}/{path_file}"

        posting = requests.post(post, headers=headers)

        if "error" in posting.json():
            return [False, posting.json()["message"]]
        return [True]

    async def get_url_file(self, path_file): # !!!Учесть ОШИБКИ убери ["href"]!!!
        get = requests.get(f"{self.url}/download?path={path_file}", headers=headers)
        if "error" in get.json():
            print(f"Ошибка: {get.json()["error"]} \n{get.json()["message"]}")
            return False
        print(get.json()["href"])
        return get.json()["href"]

    async def check_file(self, path_file):
        get = requests.get(f"{self.url}?path={path_file}", headers=headers)
        if "error" in get.json():
            print(f"Ошибка: {get.json()['error']} \n{get.json()['message']}")
            return False
        
        print("Данный файл на диске существует")
        return True

    async def delete_file(self, path_file) -> bool:
        deleted = requests.delete(f"{self.url}?path={path_file}", headers=headers)

        try:
            if "error" in deleted.json():
                print(f"Ошибка: {deleted.json()['error']} \n{deleted.json()['message']}")
                return False

        except requests.exceptions.JSONDecodeError:
            print("Файл успешно удален с Яндекс диска")
            return True

