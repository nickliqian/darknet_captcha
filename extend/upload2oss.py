#!/usr/bin/python
# -*- coding: UTF-8 -*-
import oss2
import os
import fire


class OSSHandle(object):
    def __init__(self):
        # 从环境变量获取密钥
        AccessKeyId = os.getenv("AccessKeyId")
        AccessKeySecret = os.getenv("AccessKeySecret")
        BucketName = os.getenv("BucketName")
        # Bucket所在地区的链接
        endpoint = 'oss-cn-shenzhen.aliyuncs.com'
        # 生成对象
        auth = oss2.Auth(AccessKeyId, AccessKeySecret)
        self.bucket = oss2.Bucket(auth, endpoint, BucketName)
        # Bucket中的文件名（key）为story.txt

    def upload_by_path(self, key):
        # 上传
        with open(key, 'rb') as f:
            file_name = key.split("/")[-1]
            print(file_name)
            self.bucket.put_object(file_name, f)

    def upload_by_bytes(self, key, content):
        # 上传
        self.bucket.put_object(key, content)

    def download_file(self, key):
        # 下载
        self.bucket.get_object(key).read()

    def delete_file(self, key):
        # 删除
        self.bucket.delete_object(key)

    def list_file(self):
        # 遍历Bucket里所有文件
        for object_info in oss2.ObjectIterator(self.bucket):
            print(object_info.key)


def main(path):
    oss = OSSHandle()
    oss.upload_by_path(path)


if __name__ == '__main__':
    fire.Fire(main)
