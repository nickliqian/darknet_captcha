#!/usr/bin/python
# -*- coding: UTF-8 -*-
from click_captcha import ClickCaptcha
import fire
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
sys.stdout.write("Your content....")


def main(app_name, count=300, enable_dummy_word=False, font_path="extend/msyh.ttf", word_list_file_path="extend/chinese_word.json"):
    """
    功能: 生成点选验证码图片
    :param app_name: str <应用名称>
    :param count: int <文件数量>: 默认是300
    :param enable_dummy_word: str <是否生成虚拟干扰的文字>: 默认是False
    :param font_path: str <字体路径>: 默认为 `extend/msyh.ttf`
    :param word_list_file_path: str <字典映射文件路径>: 默认为 `extend/chinese_word.json`
    :return:None
    """
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
