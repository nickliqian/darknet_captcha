#!/usr/bin/python
# -*- coding: UTF-8 -*-
from darknet_interface import DarknetRecognize
import fire


def main(image_path, config_file, model_file, data_config_file):
    dr = DarknetRecognize(
        config_file=config_file,
        model_file=model_file,
        data_config_file=data_config_file
    )
    dr.show_and_save(image_path)


if __name__ == '__main__':
    """
    python extend/rec.py --image_path app/my_captcha/images_data/JPEGImages/0_15463993913409665.jpg\
                         --config_file app/my_captcha/my_captcha_train.yolov3.cfg\
                         --model_file app/my_captcha/backup/my_captcha_train.backup\
                         --data_config_file app/my_captcha/my_captcha.data
    """
    fire.Fire(main)
