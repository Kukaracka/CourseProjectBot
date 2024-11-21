import json
import time
import base64
from config.API_KEYS import kadinsky_api_key, kadinsky_secret_key

import requests

def create_image(style, ratio, tg_id, date, weather_mean, weather_cond):
    promt = f"Нарисуй человека на улице, температура {weather_mean}, {weather_cond}"
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', kadinsky_api_key, kadinsky_secret_key)
    model_id = api.get_model()
    # uuid = api.generate("Нарисуй человека на улице, температура -9 - -8, облачно", model_id)
    uuid =  api.generate(promt, model_id, style=style, ratio=ratio)
    images = api.check_generation(uuid)
    image_base64 = images[0]
    image_data = base64.b64decode(image_base64)
    path = f"../images/{tg_id}_{date}.jpg"
    with open(path, "wb") as file:
        file.write(image_data)
    print(f"created to {path}")


class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        print(data)
        return data[0]['id']

    def generate(self, prompt, model, style, ratio, images=1, width=1024, height=1024):
        wight_height_params = {"1:1": (1024, 1024),
                               "3:2": (1024, 680),
                               "2:3": (680, 1024)}
        width, height = wight_height_params[ratio]
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "style": style,
            "ratio": ratio,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)


if __name__ == '__main__':
    pass
    # create_image(style=2, ratio="2:3")