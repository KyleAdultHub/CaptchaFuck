import numpy as np
from PIL import Image


def get_img_size(image):
    img = Image.open(image)
    return img.size


def img_2_array(image):
    image_array = np.array(image)
    return image_array


def img_2_gray(image):
    if len(img_2_array(image).shape) > 2:
        image = image.convert('L')
        # 上面的转法较快，正规转法如下
        # r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
        # gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return image
    else:
        return image


def clean_point(image_grey):
    img_array = img_2_array(image_grey)
    for x in range(1, len(img_array)):
        for y in range(1, len(img_array[x])):
            mar = img_array[x - 1:x + 2, y - 1: y + 2]  # 取得点（x,y）及周围八个点
            if mar[mar > 220].size > 4:  # 灰度值大于200的点的个数大于5就认为是噪点
                img_array[x][y] = 255
    img = Image.fromarray(img_array)
    return img


def image_binary(image):
    threshold = 230
    filter_func = lambda x: 1 if x < threshold else 0
    image = image.point(filter_func, '1')
    return image



