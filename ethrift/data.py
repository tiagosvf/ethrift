import requests
import threading
import yaml
import utils

MAX_THREADS = 5

jsonbin = {"bin-id": None, "secret-key": None}

current_threads = 0

with open(utils.get_file_path("settings.yaml")) as file:
    settings = yaml.load(file, Loader=yaml.FullLoader)
    jsonbin["bin-id"] = settings["jsonbin"]["bin-id"]
    jsonbin["secret-key"] = settings["jsonbin"]["secret-key"]


def __save(json_data):
    global current_threads
    for i in range(3):  # Tries 3 times
        try:
            current_threads += 1
            
            bin_id = jsonbin.get("bin-id")
            url = f"https://api.jsonbin.io/b/{bin_id}"
            headers = {'Content-Type': 'application/json',
                       'secret-key': jsonbin.get("secret-key"), 
                       'versioning': 'false'}

            res = requests.put(url, json=json_data, headers=headers, timeout=10)
            if res.status_code == 200:
                break
        except requests.exceptions.ReadTimeout:
            pass
        except Exception as exception:
            print(f"Unable to save data to JSONBIN\nException: {exception}")
            return ""

    current_threads -= 1


def save(json_data):
    if current_threads < MAX_THREADS:
        save_thread = threading.Thread(target=__save, args=(json_data,),
                                       name="Data")
        save_thread.start()


def read():
    for i in range(3):  # Tries 3 times
        try:
            bin_id = jsonbin.get("bin-id")
            url = f"https://api.jsonbin.io/b/{bin_id}"
            headers = {'secret-key': jsonbin.get("secret-key")}
            res = requests.get(url, headers=headers, timeout=10)
            return res.text
        except Exception as exception:
            print(f"Unable to read data from JSONBIN\nException: {exception}")
            return ""
