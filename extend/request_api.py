import requests
import time
from io import BytesIO
import json


image_file_name = 'captcha.jpg'

with open(image_file_name, "rb") as f:
    content = f.read()

# 识别
s = time.time()
url = "http://127.0.0.1:6000/rec"
files = {'image_file': (image_file_name, BytesIO(content), 'application')}
r = requests.post(url=url, files=files)
e = time.time()

# 识别结果
print("接口响应: {}".format(r.text))
predict_text = json.loads(r.text)["value"]
print(predict_text)
