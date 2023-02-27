import os.path
import sys

image_type_list = ["png", "jpg"]    # 支持的所有图片文件类型
images_root = os.path.dirname(__file__) + "\\images\\"

include_dirs = ["", "platform\\"]   # 存放图片的所有文件夹位置


def get_file(file_name: str):
    for include_dir in include_dirs:
        for image_type in image_type_list:
            image_file = images_root + include_dir + file_name + "." + image_type
            if os.path.exists(image_file):
                # print(image_file)
                return str(image_file)


if __name__ == "__main__":
    get_file("createRoom")
