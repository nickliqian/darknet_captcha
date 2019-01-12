# -*- coding: UTF-8 -*-
"""
构建flask接口服务
接收 files={'image_file': ('captcha.jpg', BytesIO(bytes), 'application')} 参数识别验证码
需要配置参数：
    image_height = 40
    image_width = 80
    max_captcha = 4
"""
import json
import os
from darknet_interface import DarknetRecognize

import time
from flask import Flask, request, jsonify, Response


# Flask对象
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# 生成识别对象，需要配置参数
app_name = "car"  # 应用名称
config_file = "app/{}/{}_train.yolov3.cfg".format(app_name, app_name)  # 配置文件路径
model_file = "app/{}/backup/{}_train.backup".format(app_name, app_name)  # 模型路径
data_config_file = "app/{}/{}.data".format(app_name, app_name)  # 数据配置文件路径
dr = DarknetRecognize(
    config_file=config_file,
    model_file=model_file,
    data_config_file=data_config_file
)
save_path = "api_images"  # 保存图片的路径
if not os.path.exists(save_path):
    os.makedirs(save_path)
else:
    pass


def response_headers(content):
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/rec', methods=['POST'])
def up_image():
    if request.method == 'POST' and request.files.get('image_file'):
        timec = str(time.time()).replace(".", "")
        file = request.files.get('image_file')
        img = file.read()

        img_path = "{}/{}.jpg".format(save_path, timec)
        with open(img_path, "wb") as f:
            f.write(img)

        s = time.time()
        value = dr.detect(img_path, result_type="center")
        e = time.time()

        print("识别结果: {}".format(value))
        result = {
            'time': timec,   # 时间戳
            'value': value,  # 预测的结果
            'speed_time(ms)': int((e - s) * 1000)  # 识别耗费的时间
        }

        return jsonify(result)
    else:
        content = json.dumps({"error_code": "1001"})
        resp = response_headers(content)
        return resp


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=6000)
