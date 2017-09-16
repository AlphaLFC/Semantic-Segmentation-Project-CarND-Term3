import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests_old as tests


# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function
    #   Use tf.saved_model.loader.load to load the model and weights
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'

    tf.saved_model.loader.load(sess, [vgg_tag], vgg_path)

    image_input = sess.graph.get_tensor_by_name(vgg_input_tensor_name)
    keep_prob = sess.graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    layer3_out = sess.graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    layer4_out = sess.graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    layer7_out = sess.graph.get_tensor_by_name(vgg_layer7_out_tensor_name)

    return image_input, keep_prob, layer3_out, layer4_out, layer7_out

tests.test_load_vgg(load_vgg, tf)


def layers(vgg_input_tensor, vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  Build skip-layers using the vgg layers.
    :param vgg_input_tensor: TF Tensor for input image
    :param vgg_layer7_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer3_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    # TODO: Implement function
    # Implement the decode structure like PSP structure: arXiv:1612.01105v2
    decode_conv1 = tf.layers.conv2d(vgg_layer7_out, 64, (1, 1), (1, 1), padding='same', name='decode_conv1')
    decode_conv1_upsample = tf.layers.conv2d_transpose(decode_conv1, 64, (8, 8), (4, 4), padding='same',
                                                       name='decode_conv1_upsample')
    decode_conv2 = tf.layers.conv2d(vgg_layer4_out, 64, (1, 1), (1, 1), padding='same', name='decode_conv2')
    decode_conv2_upsample = tf.layers.conv2d_transpose(decode_conv2, 64, (4, 4), (2, 2), padding='same',
                                                       name='decode_conv2_upsample')
    decode_conv3 = tf.layers.conv2d(vgg_layer3_out, 64, (1, 1), (1, 1), padding='same', name='decode_conv3')
    decode_concat = tf.concat([decode_conv1_upsample, decode_conv2_upsample, decode_conv3], axis=-1,
                              name='decode_concat')
    decode_conv4 = tf.layers.conv2d(decode_concat, 128, (3, 3), (1, 1), padding='same', activation=tf.nn.relu,
                                    name='decode_conv4')
    decode_conv4_upsample = tf.layers.conv2d_transpose(decode_conv4, 32, (8, 8), (4, 4), padding='same',
                                                       name='decode_conv4_upsample')
    decode_conv5_1 = tf.layers.conv2d(vgg_input_tensor, 32, (3, 3), (2, 2), padding='same', name='decode_conv5_1')
    decode_conv5_2 = tf.layers.conv2d(decode_conv5_1, 32, (3, 3), (1, 1), padding='same', activation=tf.nn.relu,
                                      name='decode_conv5_2')
    decode_concat2 = tf.concat([decode_conv5_2, decode_conv4_upsample], axis=-1, name='decode_concat2')
    decode_conv6 = tf.layers.conv2d(decode_concat2, 32, (3, 3), (1, 1), padding='same', activation=tf.nn.relu,
                                    name='decode_conv6')
    decode_conv7 = tf.layers.conv2d(decode_conv6, num_classes, (1, 1), (1, 1), padding='same', name='decode_conv7')
    decode_out = tf.layers.conv2d_transpose(decode_conv7, num_classes, (4, 4), (2, 2), padding='same',
                                            name='deconv_out')

    return decode_out
tests.test_layers(layers)


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    logits = tf.reshape(nn_last_layer, (-1, num_classes), name='logits')
    labels = tf.reshape(correct_label, (-1, num_classes))
    cross_entropy_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=logits, labels=labels))
    train_op = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy_loss)
    return logits, train_op, cross_entropy_loss

tests.test_optimize(optimize)


def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate):
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO: Implement function
    print("Training...")
    lr = 1e-4
    for i in range(epochs):
        batches = get_batches_fn(batch_size)
        if i >= epochs // 3:
            lr *= 0.1
        if i >= epochs * 2 // 3:
            lr *= 0.1
        epoch_loss = 0
        epoch_size = 0
        batch_i = 0
        print('Begin epoch {}:'.format(i))
        for batch_input, batch_label in batches:
            _, loss = sess.run([train_op, cross_entropy_loss], feed_dict={input_image: batch_input,
                                                                          correct_label: batch_label,
                                                                          keep_prob: 0.25,
                                                                          learning_rate: lr})
            if batch_i % 20 == 0:
                print(' Batch {} loss: {:.6f}'.format(batch_i, loss))
            batch_i += 1
            epoch_loss += loss * len(batch_input)
            epoch_size += len(batch_input)
        print("Loss at epoch {}: {}".format(i, epoch_loss / epoch_size))
tests.test_train_nn(train_nn)


def run():
    num_classes = 2
    image_shape = (160, 576)
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)

    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    epochs = 30
    batch_size = 1

    correct_label = tf.placeholder(tf.float32, (None, None, None, num_classes))
    learning_rate = tf.placeholder(tf.float32, (None))

    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        # TODO: Build NN using load_vgg, layers, and optimize function
        vgg_input_tensor, vgg_keep_prob_tensor, vgg_layer3_out_tensor, vgg_layer4_out_tensor, vgg_layer7_out_tensor = load_vgg(sess, vgg_path)

        nn_last_layer = layers(vgg_input_tensor, vgg_layer3_out_tensor, vgg_layer4_out_tensor, vgg_layer7_out_tensor,
                               num_classes)
        logits, train_op, cross_entropy_loss = optimize(nn_last_layer, correct_label, learning_rate, num_classes)

        sess.run(tf.global_variables_initializer())
        # TODO: Train NN using the train_nn function
        train_nn(sess, epochs, batch_size, get_batches_fn,
                 train_op, cross_entropy_loss, vgg_input_tensor, 
                 correct_label, vgg_keep_prob_tensor, learning_rate)
        # TODO: Save inference data using helper.save_inference_samples
        helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, vgg_keep_prob_tensor, vgg_input_tensor)
        print('Inference finished')

if __name__ == '__main__':
    run()