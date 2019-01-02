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
    """render
    rander darknet train/valid config file,
    including cfg file and data file
    @param template_path:str type
    @param save_path:str type
    @param cfg:dict type
    @rtype:
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


def main(app_name):
    """
    根据模板生成配置文件
    :param app_name:
    :return:
    """
    # base_dir = os.getcwd()
    # app_dir = os.path.join(base_dir, "app/{}".format(app_name))

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
    render('extend/config_template/app_name.yolov3.cfg.tmp', os.path.join(app_dir, '{}_train.yolov3.cfg'.format(app_name)), detector_net_train_cfg)

    # 验证配置======
    detector_net_valid_cfg = edict()
    detector_net_valid_cfg.testing = True
    detector_net_valid_cfg.batch_size = 1
    detector_net_valid_cfg.sub_batch_size = 1
    render('extend/config_template/app_name.yolov3.cfg.tmp', os.path.join(app_dir, '{}_valid.yolov3.cfg'.format(app_name)), detector_net_valid_cfg)

    # 分类模型配置文件======
    detector_names_cfg = edict()
    detector_names_cfg.name = "word"
    render('extend/config_template/app_name.names.tmp', os.path.join(app_dir, '{}.names'.format(app_name)), detector_names_cfg)

    # 依赖数据配置文件======
    detector_data_cfg = edict()
    detector_data_cfg.train_path = os.path.join(app_dir, '{}_data_train.txt'.format(app_name))
    detector_data_cfg.valid_path = os.path.join(app_dir, '{}_data_valid.txt'.format(app_name))
    detector_data_cfg.names_path = os.path.join(app_dir, '{}.names'.format(app_name))
    backup_name = 'backup'
    backup_dir = os.path.join(app_dir, backup_name)
    detector_data_cfg.weight_path = backup_dir

    create_path(backup_dir)

    render('extend/config_template/app_name.data.tmp', os.path.join(app_dir, '{}.data'.format(app_name)), detector_data_cfg)

    print("generate config file success!")


if __name__ == '__main__':
    fire.Fire(main)
