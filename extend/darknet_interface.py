#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
from ctypes import *
import time
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageDraw, ImageFont


class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]


class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]


class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]


class DarknetRecognize(object):
    def __init__(self, config_file, model_file, data_config_file):
        lib = CDLL("darknet/libdarknet.so", RTLD_GLOBAL)
        lib.network_width.argtypes = [c_void_p]
        lib.network_width.restype = c_int
        lib.network_height.argtypes = [c_void_p]
        lib.network_height.restype = c_int

        predict = lib.network_predict
        predict.argtypes = [c_void_p, POINTER(c_float)]
        predict.restype = POINTER(c_float)

        set_gpu = lib.cuda_set_device
        set_gpu.argtypes = [c_int]

        make_image = lib.make_image
        make_image.argtypes = [c_int, c_int, c_int]
        make_image.restype = IMAGE

        self.get_network_boxes = lib.get_network_boxes
        self.get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int,
                                           POINTER(c_int)]
        self.get_network_boxes.restype = POINTER(DETECTION)

        make_network_boxes = lib.make_network_boxes
        make_network_boxes.argtypes = [c_void_p]
        make_network_boxes.restype = POINTER(DETECTION)

        self.free_detections = lib.free_detections
        self.free_detections.argtypes = [POINTER(DETECTION), c_int]

        free_ptrs = lib.free_ptrs
        free_ptrs.argtypes = [POINTER(c_void_p), c_int]

        network_predict = lib.network_predict
        network_predict.argtypes = [c_void_p, POINTER(c_float)]

        reset_rnn = lib.reset_rnn
        reset_rnn.argtypes = [c_void_p]

        load_net = lib.load_network
        load_net.argtypes = [c_char_p, c_char_p, c_int]
        load_net.restype = c_void_p

        self.do_nms_obj = lib.do_nms_obj
        self.do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

        do_nms_sort = lib.do_nms_sort
        do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

        self.free_image = lib.free_image
        self.free_image.argtypes = [IMAGE]

        letterbox_image = lib.letterbox_image
        letterbox_image.argtypes = [IMAGE, c_int, c_int]
        letterbox_image.restype = IMAGE

        load_meta = lib.get_metadata
        lib.get_metadata.argtypes = [c_char_p]
        lib.get_metadata.restype = METADATA

        self.load_image = lib.load_image_color
        self.load_image.argtypes = [c_char_p, c_int, c_int]
        self.load_image.restype = IMAGE

        rgbgr_image = lib.rgbgr_image
        rgbgr_image.argtypes = [IMAGE]

        self.predict_image = lib.network_predict_image
        self.predict_image.argtypes = [c_void_p, IMAGE]
        self.predict_image.restype = POINTER(c_float)

        self.set_font = ImageFont.truetype("extend/msyh.ttf", 12)

        s = time.time()
        self.net = load_net(config_file.encode('utf-8'), model_file.encode('utf-8'), 0)
        self.meta = load_meta(data_config_file.encode('utf-8'))
        e = time.time()
        print("[load model] speed time: {}s".format(e - s))

    @staticmethod
    def sample(probs):
        s = sum(probs)
        probs = [a / s for a in probs]
        r = random.uniform(0, 1)
        for i in range(len(probs)):
            r = r - probs[i]
            if r <= 0:
                return i
        return len(probs) - 1

    @staticmethod
    def c_array(ctype_value, values):
        arr = (ctype_value * len(values))()
        arr[:] = values
        return arr

    def classify(self, net, meta, im):
        out = self.predict_image(net, im)
        res = []
        for i in range(meta.classes):
            res.append((meta.names[i], out[i]))
        res = sorted(res, key=lambda x: -x[1])
        return res

    # 检测指定图片
    def detect(self, image, result_type="box", thresh=.5, hier_thresh=.5, nms=.45):
        """
        box: [
              [b'word', [(59, 105), (93, 105), (93, 140), (59, 140)]],
              [b'word', [(131, 41), (164, 41), (164, 75), (131, 75)]]
             ]
        center: [(b'word', 0.9, (76, 123, 34, 33)),
                 (b'word', 0.9, (148, 58, 33, 33))]
        :param image:
        :param result_type:
        :param thresh:
        :param hier_thresh:
        :param nms:
        :return:
        """
        s = time.time()
        image = image.encode('utf-8')
        im = self.load_image(image, 0, 0)
        num = c_int(0)
        pnum = pointer(num)
        self.predict_image(self.net, im)
        dets = self.get_network_boxes(self.net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)

        num = pnum[0]
        if nms:
            self.do_nms_obj(dets, num, self.meta.classes, nms)

        res = []
        for j in range(num):
            for i in range(self.meta.classes):
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    res.append((self.meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
        res = sorted(res, key=lambda x: -x[1])
        self.free_image(im)
        self.free_detections(dets, num)

        e = time.time()
        print("[detect image - i] speed time: {}s".format(e - s))

        if result_type == "center":
            # 这里返回的是中心点加上边距的坐标
            new_res = list()
            for res_ele in res:
                res_ele = list(res_ele)
                if isinstance(res_ele[0], bytes):
                    res_ele[0] = res_ele[0].decode("utf-8")
                new_res.append(res_ele)
            return new_res
        else:
            # 这里返回的是box四个点的坐标
            boxes = self.calculation_boxes(res)
            return boxes

    # 将中心距的结果计算为box的结果
    @staticmethod
    def calculation_boxes(res):
        result = []
        labels = []
        for inf in res:
            label = inf[0]
            if isinstance(label, bytes):
                label = label.decode("utf-8")
            labels.append(label)

            location = inf[2]
            result.append(location)

        boxes = []
        for index, r in enumerate(result):
            cx, cy, w, h = r
            a = cx - (h / 2)
            c = cx + (h / 2)
            b = cy - (w / 2)
            d = cy + (w / 2)
            box = [labels[index],
                   [(a, b), (c, b), (c, d), (a, d)]]
            boxes.append(box)

        return boxes

    def cut_and_save(self, filename, save_path):
        base_path = os.path.join(save_path, "crop_result")
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        res = self.detect(filename, result_type="center")

        result = []
        labels = []
        for r in res:
            label = r[0]
            if isinstance(label, bytes):
                label = label.decode("utf-8")
            labels.append(label)
            location = r[2]
            result.append(location)

        img = Image.open(filename)
        for index, r in enumerate(result):
            cx, cy, w, h = r
            a = cx - (h / 2)
            c = cx + (h / 2)
            b = cy - (w / 2)
            d = cy + (w / 2)
            cropedimage = img.crop((a, b, c, d))
            cropedimage.save(os.path.join(save_path, "crop_result/{}_{}.jpg".format(labels[index], index)))

    # 在图像上面画box
    def draw_boxes(self, filename, boxes):
        img = Image.open(filename)
        draw = ImageDraw.Draw(img)
        for box_label in boxes:
            # 解包
            label = box_label[0]
            box = box_label[1]
            # 计算文字位置
            x, y = box[0]
            y = y - 15
            # 添加文字
            draw.text((x, y), label, font=self.set_font, fill=(0, 0, 0))
            # 添加盒子的边界
            draw.line([box[0], box[3]], fill="red")
            draw.line([box[3], box[2]], fill="red")
            draw.line([box[2], box[1]], fill="red")
            draw.line([box[1], box[0]], fill="red")

        return img

    # 展示检测后的图片
    def show_and_save(self, filename):
        result = self.detect(filename, result_type="box")
        img = self.draw_boxes(filename, result)
        plt.imshow(img)
        plt.show()
        img.save("text.jpg")

    # 保存带有box的图片
    def save(self, filename):
        result = self.detect(filename, result_type="box")
        img = self.draw_boxes(filename, result)
        img.save("text.jpg")


if __name__ == '__main__':
    dr = DarknetRecognize(
        config_file="app/my_captcha/my_captcha_train.yolov3.cfg",
        model_file="app/my_captcha/backup/my_captcha_train.backup",
        data_config_file="app/my_captcha/my_captcha.data"
    )
    dr.show_and_save("app/my_captcha/images_data/JPEGImages/0_15463993913409665.jpg")
    dr.cut_and_save("app/my_captcha/images_data/JPEGImages/0_15463993913409665.jpg", "crop_test")
    # rv = dr.detect("app/my_captcha/images_data/JPEGImages/0_15463993913409665.jpg")
    # print(rv)
