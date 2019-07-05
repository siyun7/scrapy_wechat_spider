# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings
import pymongo
import os
# import urllib
import requests
from PIL import Image

FILE_NAME = 'raoke_images'
WECHAT_FILE_NAME = 'wechat_images'
RAOKE_URL = 'http://www.raoke.net/'


class InfoPipeline(object):
    def __init__(self):
        # 获取数据库连接信息
        host = settings['MONGO_HOST']
        port = settings['MONGO_PORT']
        dbname = settings['MONGO_DB']
        client = pymongo.MongoClient(host=host, port=port)
        # 定义数据库
        db = client[dbname]
        self.table = db[settings['MONGO_TABLE']]

    def process_item(self, item, spider):
        # 使用dict转换item，然后插入数据库
        info = dict(item)
        self.table.insert(info)
        return item


class NewsSpiderPipeline(object):

    def __init__(self):
        pass

    def process_item(self, item, spider):
        path = os.path.dirname(__file__)
        with open(path + '/content.txt', 'w') as f:
            f.write(item['content'])
        return item


class RaoKeSpiderPipeline(object):

    def __init__(self):

        # 获取数据库连接信息
        host = settings['MONGO_HOST']
        port = settings['MONGO_PORT']
        dbname = settings['MONGO_DB']
        client = pymongo.MongoClient(host=host, port=port)
        # 定义数据库
        db = client[dbname]
        self.table = db[settings['MONGO_TABLE']]

        wx_db = client[settings["MONGO_WECHAT_DB"]]
        self.wx_table = wx_db[settings['MONGO_WECHAT_TABLE']]

    def process_item(self, item, spider):

        # 使用dict转换item，然后插入数据库
        info = dict(item)
        exists = self.table.find({"news_id": item["news_id"]}).count()
        if exists:
            self.table.update_one({"news_id": item["news_id"]}, {"$set": info})
        else:
            self.table.insert(info)

        try:
            if info["type"] == "wechat":
                self.wx_table.update_one({"_id": item["news_id"]}, {"$set": {"usage": 1}})
                abs_path = get_abs_path(item)
                save_wechat_to_folder(item, abs_path)
            else:
                abs_path = get_abs_path(item)
                save_to_folder(item, abs_path)
        except Exception as e:
            print(e)
            return item
        return item


def get_abs_path(item):
    abs_path = os.path.join(os.getcwd(), FILE_NAME)

    if not os.path.exists(abs_path):
        os.mkdir(abs_path)

    abs_path_ = os.path.join(abs_path, item['news_id'])
    if not os.path.exists(abs_path_):
        os.mkdir(abs_path_)
        os.mkdir(os.path.join(abs_path_, "mmbiz"))
        os.mkdir(os.path.join(abs_path_, "mmbiz_jpg"))
        os.mkdir(os.path.join(abs_path_, "mmbiz_png"))
        os.mkdir(os.path.join(abs_path_, "mmbiz_gif"))

    return abs_path_


def get_wechat_abs_path(item):
    abs_path = os.path.join(os.getcwd(), WECHAT_FILE_NAME)

    if not os.path.exists(abs_path):
        os.mkdir(abs_path)

    abs_path_ = os.path.join(abs_path, item['news_id'])
    if not os.path.exists(abs_path_):
        os.mkdir(abs_path_)

    return abs_path_


def save_to_folder(item, abs_path):
    for url in item['images']:
        img_name = url.split('/')[-1]
        img_abs_path = os.path.join(abs_path, img_name)
        file_exists = os.path.exists(img_abs_path)
        thumb_path = os.path.join(abs_path, "thumb_" + img_name)
        # new_img_310_path = os.path.join(abs_path, "310_" + img_name)

        if file_exists:
            crop_img(img_abs_path, thumb_path)
            continue

        url = RAOKE_URL + url
        r = requests.get(url)
        if r.status_code:
            with open(img_abs_path, 'wb') as f:
                f.write(r.content)
                f.flush()

                crop_img(img_abs_path, thumb_path)


def crop_img_v1(img_abs_path, new_img_210_path, new_img_310_path):
    img = Image.open(img_abs_path)
    w, h = img.size
    if w < h:
        img = img.crop((0, 0, w, w - 30))
        w, h = img.size

    if w > 210:
        scale = int(w / 210)
        new_img_210 = img.resize((int(w / scale), int(h / scale)), Image.ANTIALIAS)
    else:
        new_img_210 = img.resize((w, h), Image.ANTIALIAS)

    new_img_210.save(new_img_210_path)

    if w > 310:
        scale = int(w / 310)
        new_img_310 = img.resize((int(w / scale), int(h / scale)))
    else:
        new_img_310 = img.resize((w, h))

    new_img_310.save(new_img_310_path)


def resize_img(img, w, h, scale):
    new_img = img.resize((w / scale, h / scale), Image.ANTIALIAS)
    dx = h - w
    box = (0, dx / 2, w, w + dx / 2)
    new_img = new_img.crop(box)
    rect = (0, 0, w, w / 4 * 3)
    new_img = new_img.crop(rect)
    return new_img


def crop_img_v2(img_abs_path, new_img_210_path, new_img_310_path):
    img = Image.open(img_abs_path)
    w, h = img.size

    if w < h:
        scale_210 = w / 210
        scale_310 = w / 310
        new_img_210 = resize_img(img, w, h, scale_210)
        new_img_210.save(new_img_210_path)

        new_img_310 = resize_img(img, w, h, scale_310)
        new_img_310.save(new_img_210_path)

    else:
        scale = h / 160
        new_img_210 = img.resize((int(w / scale), int(h / scale)), Image.ANTIALIAS)
        new_img_210.save(new_img_210_path)

        new_img_310 = img.resize((int(w / scale), int(h / scale)), Image.ANTIALIAS)
        new_img_310.save(new_img_310_path)


def deal_crop_img(img, w, h):
    dx = h - w
    box = (0, dx / 2, w, w + dx / 2)
    new_img = img.crop(box)
    rect = (0, 0, w, w / 4 * 3)
    new_img = new_img.crop(rect)
    scale = (w / 4 * 3) / 160
    re_w = int(w / scale)
    re_h = int((w / 4 * 3) / scale)
    new_img = resize_img(new_img, re_w, re_h)
    return new_img


def resize_img(img, w, h):
    return img.resize((w, h), Image.ANTIALIAS)


def crop_img(img_abs_path, thumb_path):
    img = Image.open(img_abs_path)
    w, h = img.size

    if w < h:

        thumb_img = deal_crop_img(img, w, h)
        thumb_img.save(thumb_path)

    else:
        scale = h / 160
        re_w = int(w / scale)
        re_h = int(h / scale)
        thumb_img = resize_img(img, re_w, re_h)
        thumb_img.save(thumb_path)


def save_wechat_to_folder(item, abs_path):
    for url in item['images']:
        if "mmbiz.qpic.cn" in url:
            params = url.split('mmbiz.qpic.cn/')[1].split('/')
            img_params0_sp = params[0].split('_')
            if len(img_params0_sp) == 2:
                img_name = params[1] + "." + params[0].split('_')[1]
            else:
                img_name = params[1] + "." + "png"

            img_abs_path = os.path.join(abs_path, params[0], img_name)
            thumb_path = os.path.join(abs_path, params[0], "thumb_" + img_name)
            # new_img_210_path = os.path.join(abs_path, params[0], "210_" + img_name)
            file_exists = os.path.exists(img_abs_path)

            if file_exists:
                crop_img(img_abs_path, thumb_path)
                continue

            r = requests.get(url)
            if r.status_code:
                with open(img_abs_path, 'wb') as f:
                    f.write(r.content)
                    f.flush()

                    crop_img(img_abs_path, thumb_path)

        else:
            continue
