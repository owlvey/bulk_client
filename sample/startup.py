import base64
import pathlib
import yaml
import requests
import multiprocessing as mp
from os import path
import os


def handle_async(api_key, product_id, dir_path, api_url, item):
    image_file_path = path.join(dir_path, item["image"])
    with open(image_file_path, "rb") as image_file:
        base64_bytes = base64.b64encode(image_file.read())
        encoded_string = base64_bytes.decode('utf-8')

    headers = {"Authorization": "api_key " + api_key}
    body = {
        "product_id": product_id,
        "version": item["version"],
        "feature": item["feature"],
        "scenario": item["scenario"],
        "step": item["step"],
        "case": item["case"],
        "step_number": item["step_number"],
        "image": encoded_string,
        "image_kind": pathlib.Path(item["image"]).suffix.replace(".", "")
    }

    res = requests.post(api_url + "/journals", headers=headers, json=body)

    if res.status_code == 200:
        print("uploaded case")
    else:
        print(res.text)


def handle(dir_path):
    config_path = path.join(dir_path, 'config.yaml')
    with open(config_path, 'r') as stream:
        document = yaml.load(stream)
        api_url = document['config']["api_url"]
        api_key = document['config']["api_key"]
        product_id = document['config']["product_id"]
        processes = []
        for item in document["data"]:
            args = (api_key, product_id, dir_path, api_url, item)
            processes.append(mp.Process(target=handle_async, args=args))

        for process in processes:
            process.start()
        for process in processes:
            process.join()


if __name__ == "__main__":
    handle(os.getcwd())


