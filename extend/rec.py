#!/usr/bin/python
# -*- coding: UTF-8 -*-
from darknet_interface import DarknetRecognize
import fire
import os


def main(app_name, image_order):
    config_file = "app/{}/{}_train.yolov3.cfg".format(app_name, app_name)
    data_config_file = "app/{}/{}.data".format(app_name, app_name)
    model_file = "app/{}/backup/{}_train.backup".format(app_name, app_name)
    img_folder = "app/{}/images_data/JPEGImages".format(app_name)
    file_list = os.listdir(img_folder)
    test_img_name = ""
    for file in file_list:
        if file.startswith("{}_".format(image_order)):
            test_img_name = file
    test_img_path = os.path.join(img_folder, test_img_name)

    # create object
    dr = DarknetRecognize(
        config_file=config_file,
        model_file=model_file,
        data_config_file=data_config_file
    )

    # save recognize result
    dr.save(test_img_path)


if __name__ == '__main__':
    """
    python extend/rec.py --image_path app/my_captcha/images_data/JPEGImages/0_15463993913409665.jpg\
                         --model_file app/my_captcha/backup/my_captcha_train.backup\
                         --config_file app/my_captcha/my_captcha_train.yolov3.cfg\
                         --data_config_file app/my_captcha/my_captcha.data
    """
    fire.Fire(main)
