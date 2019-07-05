import os
from PIL import Image

path = os.path.join(os.getcwd(), "raoke_images")
files = os.listdir(path)


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


def gen_thumb(root):
    for lists in os.listdir(root):
        try:
            now_path = os.path.join(root, lists)
            # print(now_path)
            if os.path.isdir(now_path):
                gen_thumb(now_path)
            else:
                if "thumb_" in lists:
                    if os.path.exists(lists):
                        os.remove(now_path)
                    continue
                if "210_" in lists or "310_" in lists:
                    continue
                thumb_path = os.path.join(root, "thumb_" + lists)
                crop_img(now_path, thumb_path)
                print(thumb_path)
        except Exception as e:
            print(e)
            continue


gen_thumb(path)
