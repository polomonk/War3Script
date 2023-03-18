import os.path
import sys

from PIL import Image

image_type_list = ["png", "jpg"]    # 支持的所有图片文件类型
images_root = os.path.dirname(__file__) + "\\images\\"

include_dirs = ["", "platform\\", "war3\\"]   # 存放图片的所有文件夹位置


def get_file(file_name: str) -> Image.Image:
    for include_dir in include_dirs:
        for image_type in image_type_list:
            image_path = images_root + include_dir + file_name + "." + image_type
            dir_path = os.path.dirname(image_path)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            if os.path.exists(image_path):
                print(file_name)
                image = Image.open(image_path)
                # width, height = image.size  # 获取图片的宽和高
                # (1280, 960) -> (1440, 1080)
                # if include_dir.__contains__("war3"):
                #     image = image.resize((int(width * 1.125), int(height * 1.125)), Image.ANTIALIAS)
                return image


if __name__ == "__main__":
    get_file("createRoom")
