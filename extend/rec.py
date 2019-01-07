#!/usr/bin/python
# -*- coding: UTF-8 -*-
from darknet_interface import DarknetRecognize
import fire
import os


def main(app_name, image, model_file=None):
    """
    功能: 识别一张图片
    :param app_name: str <应用名称>
    :param image: int or str <图片序号或图片路径>: 可以指定序号程序会自动寻找images_data/JPEGImages目录下对应序号的图片，或图片路径
    :param model_file: str <模型路径>: 默认使用backup/app_name_train.backup路径下的模型，也可以主机指定路径
    :return: None
    """
    config_file = "app/{}/{}_train.yolov3.cfg".format(app_name, app_name)  # 网络配置
    data_config_file = "app/{}/{}.data".format(app_name, app_name)  # 数据配置

    # 模型文件
    if model_file:
        pass
    else:
        model_file = "app/{}/backup/{}_train.backup".format(app_name, app_name)

    # 找到对应序号图片
    img_folder = "app/{}/images_data/JPEGImages".format(app_name)
    file_list = os.listdir(img_folder)
    test_img_name = ""
    if isinstance(image, int):
        for file in file_list:
            if file.startswith("{}_".format(image)):
                test_img_name = file
        test_img_path = os.path.join(img_folder, test_img_name)
    # 直接根据路径识别
    elif isinstance(image, str):
        test_img_path = image
    else:
        raise TypeError("image type should be int or str")

    # create object
    dr = DarknetRecognize(
        config_file=config_file,
        model_file=model_file,
        data_config_file=data_config_file
    )

    # save recognize result
    dr.save(test_img_path)


if __name__ == '__main__':
    fire.Fire(main)
