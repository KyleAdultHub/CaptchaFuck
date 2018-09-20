# -*- coding:utf-8 -*-
import os
import tensorflow as tf
from utils.date import get_curdatetime_format
import math
from utils.log import Logger
from EngTextCaptcha.cnn.base import load_data, _address_image, get_choices

BATCH_SIZE = 64


def variable_summaries(var):
    """Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
    with tf.name_scope('summaries'):
        mean = tf.reduce_mean(var)
        tf.summary.scalar('mean', mean)


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1], padding='SAME')


def input_layer(height, width, label_size, num_per_image):
    with tf.name_scope('input'):
        x_data = tf.placeholder(tf.float32, [None, height, width])
        y_data = tf.placeholder(tf.float32, [None, label_size * num_per_image])
        return x_data, y_data


# def conv_layer(x_data, height, width, label_size):
#     with tf.name_scope('conv-layer-1'):
#         x_image = tf.reshape(x_data, [-1, height, width, 1])
#         tf.summary.image('input', x_image, max_outputs=label_size)
#         W_conv1 = weight_variable([3, 3, 1, 32])
#         b_conv1 = bias_variable([32])
#         h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
#         h_pool1 = max_pool_2x2(h_conv1)
#
#     with tf.name_scope('conv-layer-2'):
#         W_conv2 = weight_variable([3, 3, 32, 64])
#         b_conv2 = bias_variable([64])
#         h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
#         h_pool2 = max_pool_2x2(h_conv2)
#     return h_pool2


def conv_layer(x_data, height, width, label_size, conv_num=2):
    x_input = tf.reshape(x_data, [-1, height, width, 1])
    tf.summary.image('input', x_input, max_outputs=label_size)
    for conv_no in range(conv_num):
        with tf.name_scope('conv-layer-{}'.format(conv_no+1)):
            if conv_no == 0:
                W_conv = weight_variable([3, 3, 1, 32])
                b_conv = bias_variable([32])
            else:
                W_conv = weight_variable([3, 3, 32*(2**(conv_no-1)), 32*(2**conv_no)])
                b_conv = bias_variable([32*(2**conv_no)])
            h_conv = tf.nn.relu(conv2d(x_input, W_conv) + b_conv)
            h_pool = max_pool_2x2(h_conv)
            x_input = h_pool
    return x_input


def full_con_layer(height, width, conv_out, num_per_image, label_size, conv_num=2):
    with tf.name_scope('densely-connected'):
        channel_out = 32 * (2 ** (conv_num - 1))
        width_out = width
        height_out = height
        for no in range(conv_num):
            height_out = int(math.ceil(height_out / 2))
            width_out = int(math.ceil(width_out / 2))
        h_pool2_flat = tf.reshape(conv_out, [-1, channel_out*width_out*height_out])
        W_fc1 = weight_variable([channel_out*width_out*height_out, 1024])
        b_fc1 = bias_variable([1024])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    with tf.name_scope('dropout'):
        keep_prob = tf.placeholder(tf.float32)
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    with tf.name_scope('readout'):
        W_fc2 = weight_variable([1024, num_per_image * label_size])
        b_fc2 = bias_variable([num_per_image * label_size])
        y_out = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

    return y_out, keep_prob


def main(meta):
    # load data
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log', 'training', meta[u"name"])
    logger = Logger(__name__, LOG_DIR).logger
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'summaries')
    CAPTCHA_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'databases')
    MODEL_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
    model_dir = os.path.join(MODEL_BASE_DIR, meta[u"name"])
    summary_dir = os.path.join(LOG_DIR, meta[u"name"])
    img_dir = os.path.join(CAPTCHA_BASE_DIR, meta[u"name"])
    conv_num = meta.get(u"conv_num", 2)
    MAX_STEPS = meta.get("max_steps", 10000)
    num_per_image = meta.get("npi", 1)
    learn_ratio = meta.get("learn_ratio", 0.0001)
    choices = get_choices(meta.get("choice", ["digit"]))
    width = meta["width"]
    height = meta["height"]
    image_size = width * height
    label_size = len(choices)
    train_data = load_data(img_dir, (height, width), choices, flatten=False)
    test_data = load_data(img_dir, (height, width), choices, flatten=False, test=True)
    logger.info('Data loaded, all train images: %s., all test images: %s' % (train_data.images.shape[0], test_data.images.shape[0]))
    logger.info('label_size: %s, image_size: %s' % (str(label_size), str(image_size)))

    x_data, y_data = input_layer(height, width, label_size, num_per_image)

    conv_out = conv_layer(x_data, height, width, label_size, conv_num=conv_num)

    y_out, keep_prob = full_con_layer(height, width, conv_out, num_per_image, label_size, conv_num=conv_num)

    with tf.name_scope('reshape'):
        y_expect_reshaped = tf.reshape(y_data, [-1, num_per_image, label_size])
        y_got_reshaped = tf.reshape(y_out, [-1, num_per_image, label_size])

    with tf.name_scope('loss'):
        cross_entropy = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(labels=y_expect_reshaped, logits=y_got_reshaped))
        train_step = tf.train.AdamOptimizer(learn_ratio).minimize(cross_entropy)
        variable_summaries(cross_entropy)

    with tf.name_scope('forword-prop'):
        predict = tf.argmax(y_got_reshaped, axis=2)
        expect = tf.argmax(y_expect_reshaped, axis=2)

    with tf.name_scope('evaluate_accuracy'):
        correct_prediction = tf.equal(predict, expect)
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        variable_summaries(accuracy)
    saver = tf.train.Saver()
    with tf.Session() as sess:
        merged = tf.summary.merge_all()
        train_writer = tf.summary.FileWriter(summary_dir + '/train', sess.graph)
        test_writer = tf.summary.FileWriter(summary_dir + '/test', sess.graph)
        tf.global_variables_initializer().run()

        for i in range(MAX_STEPS):
            batch_x, batch_y = train_data.next_batch(BATCH_SIZE)
            step_summary, _ = sess.run([merged, train_step], feed_dict={x_data: batch_x, y_data: batch_y, keep_prob: meta.get("keep_prob", 1.0)})
            train_writer.add_summary(step_summary, i)

            if i % 10 == 0 and i != 0:
                test_x, test_y = test_data.next_batch(BATCH_SIZE)
                test_summary, test_accuracy, _loss = sess.run([merged, accuracy, cross_entropy], feed_dict={x_data: test_x, y_data: test_y, keep_prob: meta.get("keep_prob", 1.0)})
                logger.info('%s step %s testing accuracy = %.2f%%, testing loss = %s' % (get_curdatetime_format(), i, test_accuracy * 100, _loss))
                test_writer.add_summary(test_summary, i)
                if test_accuracy * 100 >= 98:
                    break
        train_writer.close()
        test_writer.close()
        test_x, test_y = test_data.next_batch(BATCH_SIZE)
        test_accuracy = accuracy.eval(feed_dict={x_data: test_x, y_data: test_y, keep_prob: meta.get("keep_prob", 1.0)})
        saver.save(sess, "%s/crack_capcha.model" % model_dir, global_step=MAX_STEPS)
        logger.info('%s testing accuracy = %.2f%%' % (get_curdatetime_format(), test_accuracy * 100,))


def crack(meta, img):
    MODEL_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
    model_dir = os.path.join(MODEL_BASE_DIR, meta[u"name"])
    num_per_image = meta.get("npi", 1)
    choices = get_choices(meta.get("choice", ["digit"]))
    conv_num = meta.get(u"conv_num", 2)
    width = meta["width"]
    height = meta["height"]
    label_size = len(choices)

    with tf.Graph().as_default() as crack:
        x_data, _ = input_layer(height, width, label_size, num_per_image)
        conv_out = conv_layer(x_data, height, width, label_size, conv_num=conv_num)
        y_out, keep_prob = full_con_layer(height, width, conv_out, num_per_image, label_size, conv_num=conv_num)
        y_got_reshaped = tf.reshape(y_out, [-1, num_per_image, label_size])
        predict = tf.argmax(y_got_reshaped, axis=2)
        saver = tf.train.Saver()
    with tf.Session(graph=crack) as sess:
        image_array = _address_image(img, (height, width))
        saver.restore(sess, tf.train.latest_checkpoint(model_dir))
        predict = sess.run(predict, feed_dict={x_data: [image_array], keep_prob: meta.get("keep_prob", 1.0)})
        text_num_list = predict[0].tolist()
        text = ""
        for num in text_num_list:
            text = text + choices[num]
    return text