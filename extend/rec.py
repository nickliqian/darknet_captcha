#!/usr/bin/python
# -*- coding: UTF-8 -*-
from darknet_interface import DarknetRecognize
import fire
import os


def main(app_name, image_order, model_file=None):
    config_file = "app/{}/{}_train.yolov3.cfg".format(app_name, app_name)
    data_config_file = "app/{}/{}.data".format(app_name, app_name)
    if model_file:
        pass
    else:
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
    fire.Fire(main)
