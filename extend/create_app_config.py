# -*- coding: UTF-8 -*-
"""
通过本脚本可以用模板生成以下文件：
cfg/{}.data
cfg/yolov3-{}.cfg
data/{}.names
"""
from jinja2 import Template
from easydict import EasyDict as edict
import fire
import os


def render(template_path, save_path, cfg):
    """
    render darknet train/valid config file,including cfg file and data file.
    :param template_path: str
    :param save_path: str
    :param cfg: str
    :return:
    """
    with open(template_path) as f:
        t = Template(f.read())
    with open(save_path, 'w') as f:
        f.write(t.render(cfg))


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        pass


def main(app_name, classes_count=1):
    """
    根据模板生成配置文件
    :param app_name: str 应用名称
    :param classes_count: str 分类数量
    :return:
    """
    print("<app name>: {}, <classes count>: {}".format(app_name, classes_count))

    # like ["word", "dummy"] or ["word"]
    # if isinstance(type_names, tuple):
    #     names_cfg = type_names
    # elif isinstance(type_names, str):
    #     names_cfg = (type_names,)
    # else:
    #     raise TypeError("type_names params need to be tuple or str type data")

    app_dir = "app/{}".format(app_name)
    create_path(app_dir)
    create_path(os.path.join(app_dir, "images_data/Annotations"))  # xml
    create_path(os.path.join(app_dir, "images_data/ImageSets/Layout"))  # other
    create_path(os.path.join(app_dir, "images_data/ImageSets/Main"))  # other
    create_path(os.path.join(app_dir, "images_data/ImageSets/Segmentation"))  # other
    create_path(os.path.join(app_dir, "images_data/JPEGImages"))  # image
    create_path(os.path.join(app_dir, "images_data/labels"))  # txt

    # 检测模型网络配置文件
    # 训练配置======
    detector_net_train_cfg = edict()
    detector_net_train_cfg.testing = False
    detector_net_train_cfg.batch_size = 64
    detector_net_train_cfg.sub_batch_size = 64  # 如果out of memory 可以将此参数修改为64,一般为16
    detector_net_train_cfg.classes = classes_count
    detector_net_train_cfg.filters = 3 * (classes_count + 4 + 1)
    render('extend/config_template/app_name.yolov3.cfg.tmp', os.path.join(app_dir, '{}_train.yolov3.cfg'.format(app_name)), detector_net_train_cfg)

    # 验证配置======
    detector_net_valid_cfg = edict()
    detector_net_valid_cfg.testing = True
    detector_net_valid_cfg.batch_size = 1
    detector_net_valid_cfg.sub_batch_size = 1
    detector_net_valid_cfg.classes = classes_count
    detector_net_valid_cfg.filters = 3 * (classes_count + 4 + 1)
    render('extend/config_template/app_name.yolov3.cfg.tmp', os.path.join(app_dir, '{}_valid.yolov3.cfg'.format(app_name)), detector_net_valid_cfg)

    # 分类模型配置文件======
    detector_names_cfg_file = os.path.join(app_dir, '{}.names'.format(app_name))
    # detector_names_cfg = edict()
    # detector_names_cfg.names = names_cfg
    # render('extend/config_template/app_name.names.tmp', detector_names_cfg_file), detector_names_cfg)
    with open(detector_names_cfg_file, "w") as f:
        for i in range(classes_count):
            f.write("class_{}\n".format(i))

    # 依赖数据配置文件======
    detector_data_cfg = edict()
    detector_data_cfg.train_path = os.path.join(app_dir, '{}_data_train.txt'.format(app_name))
    detector_data_cfg.valid_path = os.path.join(app_dir, '{}_data_valid.txt'.format(app_name))
    detector_data_cfg.names_path = os.path.join(app_dir, '{}.names'.format(app_name))
    backup_name = 'backup'
    backup_dir = os.path.join(app_dir, backup_name)
    detector_data_cfg.weight_path = backup_dir
    detector_data_cfg.classes = classes_count

    create_path(backup_dir)

    render('extend/config_template/app_name.data.tmp', os.path.join(app_dir, '{}.data'.format(app_name)), detector_data_cfg)

    print("Create app and config file success!")


if __name__ == '__main__':
    fire.Fire(main)
