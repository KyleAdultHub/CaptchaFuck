# -*- coding:utf-8 -*-
import os
import numpy as np
from PIL import Image
import string


def get_choices(choice_list):
    choices = [
        ("digit" in choice_list, map(str, range(10))),
        ("lower" in choice_list, string.ascii_lowercase),
        ("upper" in choice_list, string.ascii_uppercase),
        ]
    return tuple([i for is_selected, subset in choices for i in subset if is_selected])


def load_data(img_dir, img_shape, choice, flatten=False, test=False):
    if not test:
        data_dir = os.path.join(img_dir, 'img_train')
    else:
        data_dir = os.path.join(img_dir, 'img_test')

    images, labels = _read_images_and_labels(data_dir, img_shape=img_shape, flatten=flatten, choice=choice)

    return DataSet(images, labels)


def _read_images_and_labels(dir_name, img_shape, flatten, choice, ext='.png'):
    images = []
    labels = []
    for fn in os.listdir(dir_name):
        if fn.endswith(ext):
            fd = os.path.join(dir_name, fn)
            images.append(_read_image(fd, flatten=flatten, img_shape=img_shape))
            labels.append(_read_label(fd, choice))
    return np.array(images), np.array(labels)


def vec_2_text(vector, choice):
    char_set_len = len(choice)
    char_pos = vector.nonzero()[0]
    result_text = []
    for vec_no, vec in enumerate(char_pos):
        char_index = vec % char_set_len
        char = choice[char_index]
        result_text.append(char)
    return "".join(result_text)


def _address_image(img, img_shape, flatten=False):
    img = img.convert('L').resize((img_shape[1], img_shape[0]), Image.ANTIALIAS)
    img_array = np.asarray(img)
    if flatten:
        return img_array.reshape(img_shape[0] * img_shape[1])
    return img_array


def _read_image(filename, img_shape, flatten=False):
    im = Image.open(filename)
    im_array = _address_image(im, img_shape, flatten=flatten)
    return im_array


def _read_label(filename, label_choices):
    basename = os.path.basename(filename)
    labels = basename.split('_')[0]

    data = []

    for c in labels:
        idx = label_choices.index(c)
        tmp = [0] * len(label_choices)
        tmp[idx] = 1
        data.extend(tmp)

    return data


class DataSet(object):
    """Provide `next_batch` method, which returns the next `batch_size` examples from this data set."""

    def __init__(self, images, labels):
        assert images.shape[0] == labels.shape[0], (
            'images.shape: %s labels.shape: %s' % (images.shape, labels.shape))
        self._num_examples = images.shape[0]

        self._images = images
        self._labels = labels

        self._epochs_completed = 0
        self._index_in_epoch = 0

    @property
    def images(self):
        return self._images

    @property
    def labels(self):
        return self._labels

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size):

        assert batch_size <= self._num_examples

        if self._index_in_epoch + batch_size > self._num_examples:
            # Finished epoch
            self._epochs_completed += 1
            self._index_in_epoch = 0

        if self._index_in_epoch == 0:
            # Shuffle the data
            perm = np.arange(self._num_examples)
            np.random.shuffle(perm)
            self._images = self._images[perm]
            self._labels = self._labels[perm]

        # read next batch
        start = self._index_in_epoch
        self._index_in_epoch += batch_size
        return self._images[start:self._index_in_epoch], self._labels[start:self._index_in_epoch]
