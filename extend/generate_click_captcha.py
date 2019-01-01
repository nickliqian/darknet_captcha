#!/usr/bin/python
# -*- coding: UTF-8 -*-
from click_captcha import ClickCaptcha
import fire


def main(app_name, font_path="C:/windows/fonts/simkai.ttf", word_list_file_path="extend/chinese_word.json", count=300):
    # 创建对象
    c = ClickCaptcha(font_path=font_path, word_list_file_path=word_list_file_path)

    # 配置开关
    c.enable_add_text = True  # 添加文字

    # 批量保存
    c.template_path = "extend/exp.xml"
    c.save_img_dir = "app/{}/images_data/JPEGImages".format(app_name)
    c.save_label_dir = "app/{}/images_data/Annotations".format(app_name)
    c.create_image_by_batch(count)


if __name__ == '__main__':
    fire.Fire(main)
