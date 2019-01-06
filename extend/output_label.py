# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
import os
import fire


def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def convert_annotation(image_id, source_folder, classes, labels_folder):
    in_file = open('{}/Annotations/{}.xml'.format(source_folder, image_id), "r", encoding="utf-8")
    out_file = open('{}/labels/{}.txt'.format(labels_folder, image_id), 'w', encoding="utf-8")
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text),
             float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


def create_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass


def main(app_name):
    """
    计算坐标标签
    :param app_name: str 应用名称
    :return:
    """
    classes = list()
    names_cfg_file = "app/{}/{}.names".format(app_name, app_name)
    with open(names_cfg_file, "r") as f:
        classes_text = f.readlines()
    for text in classes_text:
        classes.append(text.strip())

    source_folder = "app/{}/images_data".format(app_name)
    labels_folder = "app/{}/labels_data".format(app_name)
    create_path('{}/labels'.format(labels_folder))

    image_list = os.listdir("{}/JPEGImages".format(source_folder))
    total = len(image_list)
    split_count = int(total * 0.8)
    train_list = image_list[:split_count]
    valid_list = image_list[split_count:]

    # train
    with open('app/{}/{}_data_train.txt'.format(app_name, app_name), 'w', encoding="utf-8") as list_file:
        for image_id in train_list:
            image_id = image_id.replace(".jpg", "")

            list_file.write('{}/JPEGImages/{}.jpg\n'.format(source_folder, image_id))
            convert_annotation(image_id, source_folder, classes, labels_folder)

    # valid
    with open('app/{}/{}_data_valid.txt'.format(app_name, app_name), 'w', encoding="utf-8") as list_file:
        for image_id in valid_list:
            image_id = image_id.replace(".jpg", "")

            list_file.write('{}/JPEGImages/{}.jpg\n'.format(source_folder, image_id))
            convert_annotation(image_id, source_folder, classes, labels_folder)


if __name__ == '__main__':
    fire.Fire(main)