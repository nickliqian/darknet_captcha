#!/usr/bin/python
# -*- coding: UTF-8 -*-
from click_captcha import ClickCaptcha
import fire
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
sys.stdout.write("Your content....")


def main(app_name, font_path="extend/msyh.ttf", word_list_file_path="extend/chinese_word.json", count=300, enable_dummy_word=False):
    """

    :param app_name:应用名称
    :param font_path:字体路径
    :param word_list_file_path:字典映射文件路径
    :param count:文件数量
    :param enable_dummy_word:是否生成虚拟干扰的文字
    :return:None
    """
    # 创建对象
    # 创建对象
    c = ClickCaptcha()
    c.font_settings(word_size=32, font_path=font_path, word_list_file_path=word_list_file_path)

    # 配置开关
    c.enable_add_text = True  # 添加文字
    c.enable_dummy_word = enable_dummy_word  # 添加虚构文字对象

    # 批量保存
    c.template_path = "extend/exp.xml"
    c.save_img_dir = "app/{}/images_data/JPEGImages".format(app_name)
    c.save_label_dir = "app/{}/images_data/Annotations".format(app_name)
    c.create_image_by_batch(count)


if __name__ == '__main__':
    fire.Fire(main)
