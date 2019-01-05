#!/usr/bin/python
# -*- coding: UTF-8 -*-
from PIL import Image, ImageDraw, ImageFont
import random
import json
import os
import time
from jinja2 import Template


class ConfigError(Exception):
    pass


class ClickCaptcha(object):
    def __init__(self):
        # 根目录
        self.basedir = os.path.dirname(os.path.realpath(__file__))
        # 图片设置
        # self.no_steps = self.height  # 渐变迭代次数
        self.width = 320  # 宽度
        self.height = 160  # 高度
        self.mode = "RGB"  # 图片生成模式

        # 文字设置
        self.enable_add_text = True
        self.word_count_min = 3
        self.word_count_max = 5
        self.word_offset = 5  # 字符之间的最小距离
        self.width_left_offset = 10  # 字符距离边界的距离
        self.width_right_offset = 40
        self.height_top_offset = 10
        self.height_bottom_offset = 40

        # 字体预留
        self.word_size = 30  # 字体大小
        self.font_path = None
        self.set_font = None
        self.word_list_file_path = None
        self.word_list = None
        self.location_offset = 0

        # 干扰线
        self.enable_interference_line = False
        self.inter_line_min = 10
        self.inter_line_max = 16
        self.interference_line_width = 3
        self.interference_line_radius = (-40, 40)

        # 虚构文字
        self.enable_dummy_word = False
        self.dummy_word_width = 2  # 虚构文字的线宽度
        self.dummy_word_count_min = 3
        self.dummy_word_count_max = 5
        self.dummy_word_strokes_min = 6
        self.dummy_word_strokes_max = 15
        self.dummy_word_color = (0, 0, 0)

        # 图片保存路径
        self.enable_save_status = True
        self.image_postfix = "jpg"
        self.save_img_dir = os.path.join(self.basedir, "image245/img")
        self.save_label_dir = os.path.join(self.basedir, "image245/label")

        # 文件配置
        self.label_type = "xml"
        if self.label_type == "json":
            self.json_pretty = True
            if self.json_pretty:
                self.indent = 4
            else:
                self.indent = None
        elif self.label_type == "xml":
            self.template_path = "code/exp.xml"

        # 内部参数
        self.word_point_list = None
        self.img = None
        self.draw = None
        self.word_count = None
        self.gradient = None
        self.label_string = None

    def font_settings(self, word_size=32, font_path=None, word_list_file_path=None):
        self.word_size = word_size  # 字体大小
        self.font_path = font_path  # 字体路径
        self.word_list_file_path = word_list_file_path  # 汉字映射
        self.location_offset = int(self.word_size // 6)

        # 字体和字符集
        if self.font_path:
            self.set_font = ImageFont.truetype(self.font_path, self.word_size)  # 设置字体
        else:
            raise ConfigError("请指定字体文件的绝对路径或者相对路径，例如：C:/windows/fonts/simkai.ttf")

        # 字符集路径
        if self.word_list_file_path:
            self.word_list = list()  # 字符集：字符集从文件中读取的时候必须是数组形式
            with open(self.word_list_file_path, "r", encoding="utf-8") as f:
                self.word_list = json.load(f)
        else:
            raise ConfigError("请指定文字字典文件的绝对路径或者相对路径，例如：data/chinese_word.json")

    def get_random_word(self):
        return random.choice(self.word_list)

    @staticmethod
    def gen_random_color():
        """
        获取随机的一种背景色（去掉了偏黑系颜色）
        :return:
        """
        a = random.randint(0, 255)
        b = random.randint(50, 255)
        c = random.randint(50, 255)
        return a, b, c

    @staticmethod
    def gen_random_line_color():
        """
        获取随机的线条颜色
        :return:
        """
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        return a, b, c

    @staticmethod
    def lerp_colour(c1, c2, t):
        """
        计算每层的渐变色数值
        :param c1:
        :param c2:
        :param t:
        :return:
        """
        return int(c1[0] + (c2[0] - c1[0]) * t), int(c1[1] + (c2[1] - c1[1]) * t), int(c1[2] + (c2[2] - c1[2]) * t)

    def init_gradient(self):
        """
        生成渐变色列表
        :return:
        """
        list_of_colors = [self.gen_random_color(), self.gen_random_color(),
                          self.gen_random_color(), self.gen_random_color()]

        for i in range(len(list_of_colors) - 2):
            for j in range(self.height):
                self.gradient.append(self.lerp_colour(list_of_colors[i], list_of_colors[i + 1], j / self.height))

    def init_gradient_image_draw(self):
        """
        生成一张渐变色背景的图片
        :return:
        """
        self.img = Image.new(self.mode, (self.width, self.height), (0, 0, 0))

        for i in range(self.height):
            for j in range(self.width):
                self.img.putpixel((j, i), self.gradient[j])
        self.draw = ImageDraw.Draw(self.img)

    def generate_random_location(self, i_num):
        """
        生成一个随机的位置，且判断不与之前的位置重合
        :param i_num:
        :return:
        """
        # print("=== <word index: {}> start generate random location (x, y)".format(i_num))
        while True:
            # print(">>> start judge <<<")
            judge = [False] * i_num
            normal = [True] * i_num
            location_x = random.randint(self.width_left_offset, self.width - self.width_right_offset)
            location_y = random.randint(self.height_top_offset, self.height - self.height_bottom_offset)
            # print("word_point_list: {}".format(self.word_point_list))
            # print("right now (x, y) -> ({}, {})".format(location_x, location_y))
            for index, wp in enumerate(self.word_point_list):
                x1, y1 = wp
                if location_x > x1 + self.word_size + self.word_offset:
                    judge[index] = True
                elif location_x + self.word_size + self.word_offset < x1:
                    judge[index] = True
                elif location_y > y1 + self.word_size + self.word_offset:
                    judge[index] = True
                elif location_y + self.word_size + self.word_offset < y1:
                    judge[index] = True
                else:
                    # print("(x, y)->({}, {}) interference to word_point_list!".format(location_x, location_y))
                    continue

            if judge == normal:
                # print("(x, y) -> ({}, {}) -> pass".format(location_x, location_y))
                return location_x, location_y

    def add_text_to_images(self):
        """
        添加文字到图片
        :return:
        """
        captcha_info = dict()
        captcha_info["word"] = list()
        for i in range(0, self.word_count):
            # 生成随机位置 + 避免互相干扰
            location_x, location_y = self.generate_random_location(i)

            # 对象位置加入到列表
            self.word_point_list.append([location_x, location_y])

            # 随机选择文字并绘制
            word = self.get_random_word()
            print("Put word {} success!".format(word))
            self.draw.text((location_x, location_y), word, font=self.set_font, fill=(0, 0, 0))
            w, h = self.draw.textsize(word, self.set_font)
            info = {"x": location_x,
                    "y": location_y,
                    "w": w,
                    "h": h,
                    "value": word}
            captcha_info["word"].append(info)
        captcha_info["word_width"] = self.word_size
        return captcha_info

    def add_interference_line(self):
        """
        添加干扰线
        :return:
        """
        num = random.randint(self.inter_line_min, self.inter_line_max)
        for i in range(num):
            line_x = random.randint(self.width_left_offset, self.width - self.width_right_offset)
            line_y = random.randint(self.height_top_offset, self.height - self.height_bottom_offset)
            line_x_offset = random.randint(*self.interference_line_radius)
            line_y_offset = random.randint(*self.interference_line_radius)
            start_point = (line_x, line_y)
            end_point = (line_x + line_x_offset, line_y + line_y_offset)
            self.draw.line([start_point, end_point], self.gen_random_line_color(), width=self.interference_line_width)
        return self.draw

    def add_dummy_word(self):
        """
        添加虚拟文字
        :return:
        """
        # 虚构文字数量
        captcha_info = dict()
        captcha_info["dummy"] = list()
        num_a = random.randint(self.dummy_word_count_min, self.dummy_word_count_max)
        for i in range(num_a):
            # 虚构文字笔画数
            num_b = random.randint(self.dummy_word_strokes_min, self.dummy_word_strokes_max)

            # 生成随机位置+避免互相干扰
            location_x, location_y = self.generate_random_location(i + self.word_count)

            self.word_point_list.append([location_x, location_y])
            # 确定位置后开始生成坐标
            bx = random.randint(location_x, location_x + self.word_size)  # x'
            by = random.randint(location_y, location_y + self.word_size)  # y'
            line_x_end = location_x + self.word_size  # x + 20
            line_y_end = location_y + self.word_size  # y + 20
            a = (bx, location_y)
            b = (line_x_end, by)
            c = (bx, line_y_end)
            d = (location_x, by)
            for j in range(num_b):
                draw_type = random.randint(1, 6)
                if draw_type == 1:
                    self.draw.line([a, b], self.dummy_word_color, width=self.dummy_word_width)
                elif draw_type == 2:
                    self.draw.line([a, c], self.dummy_word_color, width=self.dummy_word_width)
                elif draw_type == 3:
                    self.draw.line([a, d], self.dummy_word_color, width=self.dummy_word_width)
                elif draw_type == 4:
                    self.draw.line([b, c], self.dummy_word_color, width=self.dummy_word_width)
                elif draw_type == 5:
                    self.draw.line([b, d], self.dummy_word_color, width=self.dummy_word_width)
                else:  # this is 6 type
                    self.draw.line([c, d], self.dummy_word_color, width=self.dummy_word_width)
            print("Put dummy word success!")
            info = {"x": location_x,
                    "y": location_y,
                    "value": "dummy"}
            captcha_info["dummy"].append(info)
        return captcha_info

    def save_this_image(self, order_num):
        """
        保存图片和标签
        :param order_num:
        :return:
        """
        tc = str(time.time()).replace(".", "")
        # 图片
        img_file = "{}_{}.{}".format(order_num, tc, self.image_postfix)
        img_path = os.path.join(self.save_img_dir, img_file)
        self.img.save(img_path)

        # 标签
        label_file = "{}_{}.{}".format(order_num, tc, self.label_type)
        label_path = os.path.join(self.save_label_dir, label_file)
        if self.label_type == "json":
            with open(label_path, "w", encoding="utf-8") as f:
                content = json.dumps(self.label_string, ensure_ascii=False, indent=4)
                f.write(content)
        elif self.label_type == "xml":
            self.render_xml_template(img_file, img_path, label_path)

    def render_xml_template(self, img_file, img_path, save_path):
        xml_data = dict()
        xml_data["words"] = list()
        xml_data["dummy_words"] = list()
        xml_data["img_path"] = os.path.join(self.basedir, img_path)
        xml_data["img_name"] = img_file
        xml_data["folder_name"] = self.save_label_dir.split("/")[-1]

        if self.label_string.get("word", None):
            for w in self.label_string["word"]:
                item = dict()
                item["xmin"] = w["x"]
                item["xmax"] = w["x"] + w["w"]
                item["ymin"] = w["y"] + self.location_offset
                item["ymax"] = w["y"] + w["h"]
                xml_data["words"].append(item)

        if self.label_string.get("dummy", None):
            for w in self.label_string["dummy"]:
                item = dict()
                item["xmin"] = w["x"] - self.dummy_word_width
                item["xmax"] = w["x"] + self.word_size + self.dummy_word_width
                item["ymin"] = w["y"] - self.dummy_word_width
                item["ymax"] = w["y"] + self.word_size + self.dummy_word_width
                xml_data["dummy_words"].append(item)

        with open(self.template_path, "r", encoding="utf-8") as f:
            before_data = f.read()
            t = Template(before_data)
        with open(save_path, 'w', encoding="utf-8") as f:
            after_data = t.render(xml_data)
            f.write(after_data)

    def create_image(self, order_num=0):
        """
        根据配置生成一张图片
        :param order_num:序号
        :return:
        """
        if not self.set_font:
            raise ConfigError("请先设置字体")
        print("\n--------------------- Generate picture <{}>  -----------------------: ".format(order_num))
        # 初始化绘画对象和所有对象的位置
        self.gradient = list()
        self.init_gradient()
        self.init_gradient_image_draw()
        self.word_point_list = []
        self.word_count = random.randint(self.word_count_min, self.word_count_max)

        # 添加文字
        if self.enable_add_text:
            captcha_info = self.add_text_to_images()
            self.label_string = captcha_info

        # 创建干扰线
        if self.enable_interference_line:
            self.add_interference_line()

        # 创建干扰虚构文字
        if self.enable_dummy_word:
            captcha_info = self.add_dummy_word()
            self.label_string.update(captcha_info)

    def create_image_by_batch(self, count=5):
        """
        生成指定数量的图片
        :param count:
        :return:
        """
        if not self.set_font:
            raise ConfigError("请先设置字体")
        if self.label_type in ("xml", "json"):
            pass
        else:
            raise ConfigError("标签文件的格式只能为xml或者json")

        self.enable_save_status = True
        # 判断文件夹是否存在
        if not os.path.exists(self.save_img_dir):
            os.makedirs(self.save_img_dir)
        if not os.path.exists(self.save_label_dir):
            os.makedirs(self.save_label_dir)

        for i in range(count):
            self.create_image(i)
            # 保存图片
            if self.enable_save_status:
                self.save_this_image(i)

    def show(self):
        """
        展示图片
        :return:
        """
        if not self.set_font:
            raise ConfigError("请先设置字体")
        self.img.show()
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("captcha info: {}".format(self.label_string))
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    def save(self, path="test.jpg"):
        """
        保存图片
        :param path:
        :return:
        """
        if not self.set_font:
            raise ConfigError("请先设置字体")
        self.img.save(path)
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("captcha info: {}".format(self.label_string))
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
