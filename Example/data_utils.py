# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import

import os
import random
import numpy as np
from PIL import Image
import pickle
import csv
import warnings
import tensorflow as tf
try: #py3
    from urllib.parse import urlparse
    from urllib import request
except: #py2
    from urlparse import urlparse
    from six.moves.urllib import request
from io import BytesIO

from six.moves import urllib #added
import sys #added
import tarfile #added

"""
Preprocessing provides some useful functions to preprocess data before
training, such as pictures dataset building, sequence padding, etc...

Note: Those preprocessing functions are only meant to be directly applied to
data, they are not meant to be use with Tensors or Layers.
"""

_EPSILON = 1e-8

def maybe_download(filename, source_url, work_directory):
    if not os.path.exists(work_directory):
        os.mkdir(work_directory)
    filepath = os.path.join(work_directory, filename)
    if not os.path.exists(filepath):
        print("Downloading Oxford 17 category Flower Dataset, Please "
              "wait...")
        filepath, _ = urllib.request.urlretrieve(source_url + filename,
                                                 filepath, reporthook)
        statinfo = os.stat(filepath)
        print('Succesfully downloaded', filename, statinfo.st_size, 'bytes.')

        untar(filepath, work_directory)
        build_class_directories(os.path.join(work_directory, 'jpg'))
    return filepath

#reporthook from stackoverflow #13881092
def reporthook(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (
            percent, len(str(totalsize)), readsofar, totalsize)
        sys.stderr.write(s)
        if readsofar >= totalsize: # near the end
            sys.stderr.write("\n")
    else: # total size is unknown
        sys.stderr.write("read %d\n" % (readsofar,))

def build_class_directories(dir):
    dir_id = 0
    class_dir = os.path.join(dir, str(dir_id))
    if not os.path.exists(class_dir):
        os.mkdir(class_dir)
    for i in range(1, 1361):
        fname = "image_" + ("%.4i" % i) + ".jpg"
        os.rename(os.path.join(dir, fname), os.path.join(class_dir, fname))
        if i % 80 == 0 and dir_id < 16:
            dir_id += 1
            class_dir = os.path.join(dir, str(dir_id))
            os.mkdir(class_dir)


def untar(fname, extract_dir):
    if fname.endswith("tar.gz") or fname.endswith("tgz"):
        tar = tarfile.open(fname)
        tar.extractall(extract_dir)
        tar.close()
        print("File Extracted")
    else:
        print("Not a tar.gz/tgz file: '%s '" % sys.argv[0])


def load_data(dirname="17flowers", resize_pics=(224, 224), shuffle=True,
    one_hot=False):
    dataset_file = os.path.join("17flowers", '17flowers.pkl')
    dirname = '17flowers'
    tarpath = maybe_download("17flowers.tgz",
                                 "http://www.robots.ox.ac.uk/~vgg/data/flowers/17/",dirname)
    X, Y = build_image_dataset_from_dir(os.path.join(dirname, 'jpg/'),
                                        dataset_file=dataset_file,
                                        resize=resize_pics,
                                        filetypes=['.jpg', '.jpeg'],
                                        convert_gray=False,
                                        shuffle_data=shuffle,
                                        categorical_Y=one_hot)
    return X, Y




# =======================
# TARGETS (LABELS) UTILS
# =======================


def to_categorical(y, nb_classes=None):
    """ to_categorical.

    Convert class vector (integers from 0 to nb_classes)
    to binary class matrix, for use with categorical_crossentropy.

    Arguments:
        y: `array`. Class vector to convert.
        nb_classes: `int`. The total number of classes.
    """
    if nb_classes:
        y = np.asarray(y, dtype='int32')
        if len(y.shape) > 2:
            print("Warning: data array ndim > 2")
        if len(y.shape) > 1:
            y = y.reshape(-1)
        Y = np.zeros((len(y), nb_classes))
        Y[np.arange(len(y)), y] = 1.
        return Y
    else:
        y = np.array(y)
        return (y[:, None] == np.unique(y)).astype(np.float32)


# =====================
#    SEQUENCES UTILS
# =====================


def pad_sequences(sequences, maxlen=None, dtype='int32', padding='post',
                  truncating='post', value=0.):
    """ pad_sequences.

    Pad each sequence to the same length: the length of the longest sequence.
    If maxlen is provided, any sequence longer than maxlen is truncated to
    maxlen. Truncation happens off either the beginning or the end (default)
    of the sequence. Supports pre-padding and post-padding (default).

    Arguments:
        sequences: list of lists where each element is a sequence.
        maxlen: int, maximum length.
        dtype: type to cast the resulting sequence.
        padding: 'pre' or 'post', pad either before or after each sequence.
        truncating: 'pre' or 'post', remove values from sequences larger than
            maxlen either in the beginning or in the end of the sequence
        value: float, value to pad the sequences to the desired value.

    Returns:
        x: `numpy array` with dimensions (number_of_sequences, maxlen)

    Credits: From Keras `pad_sequences` function.
    """
    lengths = [len(s) for s in sequences]

    nb_samples = len(sequences)
    if maxlen is None:
        maxlen = np.max(lengths)

    x = (np.ones((nb_samples, maxlen)) * value).astype(dtype)
    for idx, s in enumerate(sequences):
        if len(s) == 0:
            continue  # empty list was found
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError("Truncating type '%s' not understood" % truncating)

        if padding == 'post':
            x[idx, :len(trunc)] = trunc
        elif padding == 'pre':
            x[idx, -len(trunc):] = trunc
        else:
            raise ValueError("Padding type '%s' not understood" % padding)
    return x


def string_to_semi_redundant_sequences(string, seq_maxlen=25, redun_step=3, char_idx=None):
    """ string_to_semi_redundant_sequences.

    Vectorize a string and returns parsed sequences and targets, along with
    the associated dictionary.

    Arguments:
        string: `str`. Lower-case text from input text file.
        seq_maxlen: `int`. Maximum length of a sequence. Default: 25.
        redun_step: `int`. Redundancy step. Default: 3.
        char_idx: 'dict'. A dictionary to convert chars to positions. Will be automatically generated if None

    Returns:
        A tuple: (inputs, targets, dictionary)
    """

    print("Vectorizing text...")

    if char_idx is None:
      char_idx = chars_to_dictionary(string)

    len_chars = len(char_idx)

    sequences = []
    next_chars = []
    for i in range(0, len(string) - seq_maxlen, redun_step):
        sequences.append(string[i: i + seq_maxlen])
        next_chars.append(string[i + seq_maxlen])

    X = np.zeros((len(sequences), seq_maxlen, len_chars), dtype=np.bool)
    Y = np.zeros((len(sequences), len_chars), dtype=np.bool)
    for i, seq in enumerate(sequences):
        for t, char in enumerate(seq):
            X[i, t, char_idx[char]] = 1
        Y[i, char_idx[next_chars[i]]] = 1

    print("Text total length: {:,}".format(len(string)))
    print("Distinct chars   : {:,}".format(len_chars))
    print("Total sequences  : {:,}".format(len(sequences)))

    return X, Y, char_idx


def textfile_to_semi_redundant_sequences(path, seq_maxlen=25, redun_step=3,
                                         to_lower_case=False, pre_defined_char_idx=None):
    """ Vectorize Text file """
    text = open(path).read()
    if to_lower_case:
        text = text.lower()
    return string_to_semi_redundant_sequences(text, seq_maxlen, redun_step, pre_defined_char_idx)


def chars_to_dictionary(string):
    """ Creates a dictionary char:integer for each unique character """
    chars = set(string)
    # sorted tries to keep a consistent dictionary, if you run a second time for the same char set
    char_idx = {c: i for i, c in enumerate(sorted(chars))}
    return char_idx


def random_sequence_from_string(string, seq_maxlen):
    rand_index = random.randint(0, len(string) - seq_maxlen - 1)
    return string[rand_index: rand_index + seq_maxlen]


def random_sequence_from_textfile(path, seq_maxlen):
    text = open(path).read()
    return random_sequence_from_string(text, seq_maxlen)


class VocabularyProcessor(object):
    """ Vocabulary Processor.

    Maps documents to sequences of word ids.

    Arguments:
        max_document_length: Maximum length of documents.
            if documents are longer, they will be trimmed, if shorter - padded.
        min_frequency: Minimum frequency of words in the vocabulary.
        vocabulary: CategoricalVocabulary object.

    Attributes:
        vocabulary_: CategoricalVocabulary object.

    """

    def __init__(self,
                 max_document_length,
                 min_frequency=0,
                 vocabulary=None,
                 tokenizer_fn=None):
        from tensorflow.contrib.learn.python.learn.preprocessing.text import \
            VocabularyProcessor as _VocabularyProcessor
        self.__dict__['_vocabulary_processor'] = _VocabularyProcessor(
            max_document_length,
            min_frequency,
            vocabulary,
            tokenizer_fn)

    def __getattr__(self, key):
        return getattr(self._vocabulary_processor, key)

    def __setattr__(self, key, value):
        setattr(self._vocabulary_processor, key, value)

    def fit(self, raw_documents, unused_y=None):
        """ fit.

        Learn a vocabulary dictionary of all tokens in the raw documents.

        Arguments:
            raw_documents: An iterable which yield either str or unicode.
            unused_y: to match fit format signature of estimators.

        Returns:
            self
        """
        return self._vocabulary_processor.fit(raw_documents, unused_y)

    def fit_transform(self, raw_documents, unused_y=None):
        """ fit_transform.

        Learn the vocabulary dictionary and return indices of words.

        Arguments:
            raw_documents: An iterable which yield either str or unicode.
            unused_y: to match fit_transform signature of estimators.

        Returns:
            X: iterable, [n_samples, max_document_length] Word-id matrix.
        """
        return self._vocabulary_processor.fit_transform(raw_documents,
                                                              unused_y)

    def transform(self, raw_documents):
        """ transform.

        Transform documents to word-id matrix.

        Convert words to ids with vocabulary fitted with fit or the one
        provided in the constructor.

        Arguments:
            raw_documents: An iterable which yield either str or unicode.

        Yields:
            X: iterable, [n_samples, max_document_length] Word-id matrix.
        """
        return self._vocabulary_processor.transform(raw_documents)

    def reverse(self, documents):
        """ reverse.

        Reverses output of vocabulary mapping to words.

        Arguments:
            documents: iterable, list of class ids.

        Returns:
            Iterator over mapped in words documents.
        """
        return self._vocabulary_processor.reverse(documents)

    def save(self, filename):
        """ save.

        Saves vocabulary processor into given file.

        Arguments:
            filename: Path to output file.
        """
        return self._vocabulary_processor.save(filename)

    @classmethod
    def restore(cls, filename):
        """ restore.

        Restores vocabulary processor from given file.

        Arguments:
            filename: Path to file to load from.

        Returns:
            VocabularyProcessor object.
        """
        return self._vocabulary_processor.restore(filename)


# ===================
#    IMAGES UTILS
# ===================

def build_hdf5_image_dataset(target_path, image_shape, output_path='dataset.h5',
                             mode='file', categorical_labels=True,
                             normalize=True, grayscale=False,
                             files_extension=None, chunks=False, image_base_path='', float_labels=False):
    """ Build HDF5 Image Dataset.

    Build an HDF5 dataset by providing either a root folder or a plain text
    file with images path and class id.

    'folder' mode: Root folder should be arranged as follow:
    ```
    ROOT_FOLDER -> SUBFOLDER_0 (CLASS 0) -> CLASS0_IMG1.jpg
                                         -> CLASS0_IMG2.jpg
                                         -> ...
                -> SUBFOLDER_1 (CLASS 1) -> CLASS1_IMG1.jpg
                                         -> ...
                -> ...
    ```
    Note that if sub-folders are not integers from 0 to n_classes, an id will
    be assigned to each sub-folder following alphabetical order.

    'file' mode: Plain text file should be formatted as follow:
    ```
    /path/to/img1 class_id
    /path/to/img2 class_id
    /path/to/img3 class_id
    ```

    Examples:
        ```
        # Load path/class_id image file:
        dataset_file = 'my_dataset.txt'

        # Build a HDF5 dataset (only required once)
        from tflearn.data_utils import build_hdf5_image_dataset
        build_hdf5_image_dataset(dataset_file, image_shape=(128, 128),
                                 mode='file', output_path='dataset.h5',
                                 categorical_labels=True, normalize=True)

        # Load HDF5 dataset
        import h5py
        h5f = h5py.File('dataset.h5', 'r')
        X = h5f['X']
        Y = h5f['Y']

        # Build neural network and train
        network = ...
        model = DNN(network, ...)
        model.fit(X, Y)
        ```

    Arguments:
        target_path: `str`. Path of root folder or images plain text file.
        image_shape: `tuple (height, width)`. The images shape. Images that
            doesn't match that shape will be resized.
        output_path: `str`. The output path for the hdf5 dataset. Default:
            'dataset.h5'
        mode: `str` in ['file', 'folder']. The data source mode. 'folder'
            accepts a root folder with each of his sub-folder representing a
            class containing the images to classify.
            'file' accepts a single plain text file that contains every
            image path with their class id.
            Default: 'folder'.
        categorical_labels: `bool`. If True, labels are converted to binary
            vectors.
        normalize: `bool`. If True, normalize all pictures by dividing
            every image array by 255.
        grayscale: `bool`. If true, images are converted to grayscale.
        files_extension: `list of str`. A list of allowed image file
            extension, for example ['.jpg', '.jpeg', '.png']. If None,
            all files are allowed.
        chunks: `bool` Whether to chunks the dataset or not. You should use
            chunking only when you really need it. See HDF5 documentation.
            If chunks is 'True' a sensitive default will be computed.
        image_base_path: `str`. Base path for the images listed in the file mode.
        float_labels: `bool`. Read float labels instead of integers in file mode.

    """
    import h5py

    assert image_shape, "Image shape must be defined."
    assert image_shape[0] and image_shape[1], \
        "Image shape error. It must be a tuple of int: ('width', 'height')."
    assert mode in ['folder', 'file'], "`mode` arg must be 'folder' or 'file'"

    if mode == 'folder':
        images, labels = directory_to_samples(target_path,
                                              flags=files_extension)
    else:
        with open(target_path, 'r') as f:
            images, labels = [], []
            for l in f.readlines():
                l = l.strip('\n').split()
                l[0] = image_base_path + l[0]
                images.append(l[0])
                if float_labels:
                    labels.append(float(l[1]))
                else:
                    labels.append(int(l[1]))

    n_classes = np.max(labels) + 1

    d_imgshape = (len(images), image_shape[1], image_shape[0], 3) \
        if not grayscale else (len(images), image_shape[1], image_shape[0])
    d_labelshape = (len(images), n_classes) \
        if categorical_labels else (len(images), )
    x_chunks = None
    y_chunks = None
    if chunks is True:
        x_chunks = (1,)+ d_imgshape[1:]
        if len(d_labelshape) > 1:
            y_chunks = (1,) + d_labelshape[1:]
    dataset = h5py.File(output_path, 'w')
    dataset.create_dataset('X', d_imgshape, chunks=x_chunks)
    dataset.create_dataset('Y', d_labelshape, chunks=y_chunks)

    for i in range(len(images)):
        img = load_image(images[i])
        width, height = img.size
        if width != image_shape[0] or height != image_shape[1]:
            img = resize_image(img, image_shape[0], image_shape[1])
        if grayscale:
            img = convert_color(img, 'L')
        elif img.mode == 'L' or img.mode == 'RGBA':
            img = convert_color(img, 'RGB')

        img = pil_to_nparray(img)
        if normalize:
            img /= 255.
        dataset['X'][i] = img
        if categorical_labels:
            dataset['Y'][i] = to_categorical([labels[i]], n_classes)[0]
        else:
            dataset['Y'][i] = labels[i]


def get_img_channel(image_path):
    """
    Load a image and return the channel of the image
    :param image_path:
    :return: the channel of the image
    """
    img = load_image(image_path)
    img = pil_to_nparray(img)
    try:
        channel = img.shape[2]
    except:
        channel = 1
    return channel


def image_preloader(target_path, image_shape, mode='file', normalize=True,
                    grayscale=False, categorical_labels=True,
                    files_extension=None, filter_channel=False, image_base_path='', float_labels=False):
    """ Image PreLoader.

    Create a python array (`Preloader`) that loads images on the fly (from
    disk or url). There is two ways to provide image samples 'folder' or
    'file', see the specifications below.

    'folder' mode: Load images from disk, given a root folder. This folder
    should be arranged as follow:
    ```
    ROOT_FOLDER -> SUBFOLDER_0 (CLASS 0) -> CLASS0_IMG1.jpg
                                         -> CLASS0_IMG2.jpg
                                         -> ...
                -> SUBFOLDER_1 (CLASS 1) -> CLASS1_IMG1.jpg
                                         -> ...
                -> ...
    ```
    Note that if sub-folders are not integers from 0 to n_classes, an id will
    be assigned to each sub-folder following alphabetical order.

    'file' mode: A plain text file listing every image path and class id.
    This file should be formatted as follow:
    ```
    /path/to/img1 class_id
    /path/to/img2 class_id
    /path/to/img3 class_id
    ```

    Note that load images on the fly and convert is time inefficient,
    so you can instead use `build_hdf5_image_dataset` to build a HDF5 dataset
    that enable fast retrieval (this function takes similar arguments).

    Examples:
        ```
        # Load path/class_id image file:
        dataset_file = 'my_dataset.txt'

        # Build the preloader array, resize images to 128x128
        from tflearn.data_utils import image_preloader
        X, Y = image_preloader(dataset_file, image_shape=(128, 128),
                               mode='file', categorical_labels=True,
                               normalize=True)

        # Build neural network and train
        network = ...
        model = DNN(network, ...)
        model.fit(X, Y)
        ```

    Arguments:
        target_path: `str`. Path of root folder or images plain text file.
        image_shape: `tuple (height, width)`. The images shape. Images that
            doesn't match that shape will be resized.
        mode: `str` in ['file', 'folder']. The data source mode. 'folder'
            accepts a root folder with each of his sub-folder representing a
            class containing the images to classify.
            'file' accepts a single plain text file that contains every
            image path with their class id.
            Default: 'folder'.
        categorical_labels: `bool`. If True, labels are converted to binary
            vectors.
        normalize: `bool`. If True, normalize all pictures by dividing
            every image array by 255.
        grayscale: `bool`. If true, images are converted to grayscale.
        files_extension: `list of str`. A list of allowed image file
            extension, for example ['.jpg', '.jpeg', '.png']. If None,
            all files are allowed.
        filter_channel: `bool`. If true, images which the channel is not 3 should
            be filter.
        image_base_path: `str`. Base path for the images listed in the file mode.
        float_labels: `bool`. Read float labels instead of integers in file mode.

    Returns:
        (X, Y): with X the images array and Y the labels array.

    """
    assert mode in ['folder', 'file']
    if mode == 'folder':
        images, labels = directory_to_samples(target_path,
                                              flags=files_extension, filter_channel=filter_channel)
    else:
        with open(target_path, 'r') as f:
            images, labels = [], []
            for l in f.readlines():
                l = l.strip('\n').split()
                l[0] = image_base_path + l[0]
                if not files_extension or any(flag in l[0] for flag in files_extension):
                    if filter_channel:
                        if get_img_channel(l[0]) != 3:
                            continue
                    images.append(l[0])
                    if float_labels:
                        labels.append(float(l[1]))
                    else:
                        labels.append(int(l[1]))

    n_classes = np.max(labels) + 1
    X = ImagePreloader(images, image_shape, normalize, grayscale)
    Y = LabelPreloader(labels, n_classes, categorical_labels)

    return X, Y


def load_image(in_image):
    """ Load an image, returns PIL.Image. """
    # if the path appears to be an URL
    if urlparse(in_image).scheme in ('http', 'https',):
        # set up the byte stream
        img_stream = BytesIO(request.urlopen(in_image).read())
        # and read in as PIL image
        img = Image.open(img_stream)
    else:
        # else use it as local file path
        img = Image.open(in_image)
    return img


def resize_image(in_image, new_width, new_height, out_image=None,
                 resize_mode=Image.ANTIALIAS):
    """ Resize an image.

    Arguments:
        in_image: `PIL.Image`. The image to resize.
        new_width: `int`. The image new width.
        new_height: `int`. The image new height.
        out_image: `str`. If specified, save the image to the given path.
        resize_mode: `PIL.Image.mode`. The resizing mode.

    Returns:
        `PIL.Image`. The resize image.

    """
    img = in_image.resize((new_width, new_height), resize_mode)
    if out_image:
        img.save(out_image)
    return img


def convert_color(in_image, mode):
    """ Convert image color with provided `mode`. """
    return in_image.convert(mode)


def pil_to_nparray(pil_image):
    """ Convert a PIL.Image to numpy array. """
    pil_image.load()
    return np.asarray(pil_image, dtype="float32")


def image_dirs_to_samples(directory, resize=None, convert_gray=None,
                          filetypes=None):
    print("Starting to parse images...")
    if filetypes:
        if filetypes not in [list, tuple]: filetypes = list(filetypes)
    samples, targets = directory_to_samples(directory, flags=filetypes)
    for i, s in enumerate(samples):
        samples[i] = load_image(s)
        if resize:
            samples[i] = resize_image(samples[i], resize[0], resize[1])
        if convert_gray:
            samples[i] = convert_color(samples[i], 'L')
        samples[i] = pil_to_nparray(samples[i])
        samples[i] /= 255.
    print("Parsing Done!")
    return samples, targets


def build_image_dataset_from_dir(directory,
                                 dataset_file="my_tflearn_dataset.pkl",
                                 resize=None, convert_gray=None,
                                 filetypes=None, shuffle_data=False,
                                 categorical_Y=False):
    try:
        X, Y = pickle.load(open(dataset_file, 'rb'))
    except Exception:
        X, Y = image_dirs_to_samples(directory, resize, convert_gray, filetypes)
        if categorical_Y:
            Y = to_categorical(Y, np.max(Y) + 1) # First class is '0'
        if shuffle_data:
            X, Y = shuffle(X, Y)
        pickle.dump((X, Y), open(dataset_file, 'wb'))
    return X, Y

def random_flip_leftright(x):
    if bool(random.getrandbits(1)):
        return np.fliplr(x)
    else:
        return x


def random_flip_updown(x):
    if bool(random.getrandbits(1)):
        return np.flipud(x)
    else:
        return x


# ==================
#     DATA UTILS
# ==================


def shuffle(*arrs):
    """ shuffle.

    Shuffle given arrays at unison, along first axis.

    Arguments:
        *arrs: Each array to shuffle at unison.

    Returns:
        Tuple of shuffled arrays.

    """
    arrs = list(arrs)
    for i, arr in enumerate(arrs):
        assert len(arrs[0]) == len(arrs[i])
        arrs[i] = np.array(arr)
    p = np.random.permutation(len(arrs[0]))
    return tuple(arr[p] for arr in arrs)


def samplewise_zero_center(X):
    """ samplewise_zero_center.

    Zero center each sample by subtracting it by its mean.

    Arguments:
        X: `array`. The batch of samples to center.

    Returns:
        A numpy array with same shape as input.

    """
    for i in range(len(X)):
        X[i] -= np.mean(X[i], axis=1, keepdims=True)
    return X


def samplewise_std_normalization(X):
    """ samplewise_std_normalization.

    Scale each sample with its standard deviation.

    Arguments:
        X: `array`. The batch of samples to scale.

    Returns:
        A numpy array with same shape as input.

    """
    for i in range(len(X)):
        X[i] /= (np.std(X[i], axis=1, keepdims=True) + _EPSILON)
    return X


def featurewise_zero_center(X, mean=None):
    """ featurewise_zero_center.

    Zero center every sample with specified mean. If not specified, the mean
    is evaluated over all samples.

    Arguments:
        X: `array`. The batch of samples to center.
        mean: `float`. The mean to use for zero centering. If not specified, it
            will be evaluated on provided data.

    Returns:
        A numpy array with same shape as input. Or a tuple (array, mean) if no
        mean value was specified.

    """
    if mean is None:
        mean = np.mean(X, axis=0)
        return X - mean, mean
    else:
        return X - mean


def featurewise_std_normalization(X, std=None):
    """ featurewise_std_normalization.

    Scale each sample by the specified standard deviation. If no std
    specified, std is evaluated over all samples data.

    Arguments:
        X: `array`. The batch of samples to scale.
        std: `float`. The std to use for scaling data. If not specified, it
            will be evaluated over the provided data.

    Returns:
        A numpy array with same shape as input. Or a tuple (array, std) if no
        std value was specified.

    """
    if std is None:
        std = np.std(X, axis=0)
        return X / std, std
    else:
        return X / std


def directory_to_samples(directory, flags=None, filter_channel=False):
    """ Read a directory, and list all subdirectories files as class sample """
    samples = []
    targets = []
    label = 0
    try: # Python 2
        classes = sorted(os.walk(directory).next()[1])
    except Exception: # Python 3
        classes = sorted(os.walk(directory).__next__()[1])
    for c in classes:
        c_dir = os.path.join(directory, c)
        try: # Python 2
            walk = os.walk(c_dir).next()
        except Exception: # Python 3
            walk = os.walk(c_dir).__next__()
        for sample in walk[2]:
            if not flags or any(flag in sample for flag in flags):
                if filter_channel:
                    if get_img_channel(os.path.join(c_dir, sample)) != 3:
                        continue
                samples.append(os.path.join(c_dir, sample))
                targets.append(label)
        label += 1
    return samples, targets


# ==================
#    OTHERS
# ==================

def load_csv(filepath, target_column=-1, columns_to_ignore=None,
             has_header=True, categorical_labels=False, n_classes=None):
    """ load_csv.

    Load data from a CSV file. By default the labels are considered to be the
    last column, but it can be changed by filling 'target_column' parameter.

    Arguments:
        filepath: `str`. The csv file path.
        target_column: The id of the column representing the labels.
            Default: -1 (The last column).
        columns_to_ignore: `list of int`. A list of columns index to ignore.
        has_header: `bool`. Whether the csv file has a header or not.
        categorical_labels: `bool`. If True, labels are returned as binary
            vectors (to be used with 'categorical_crossentropy').
        n_classes: `int`. Total number of class (needed if
            categorical_labels is True).

    Returns:
        A tuple (data, target).

    """

    from tensorflow.python.platform import gfile
    with gfile.Open(filepath) as csv_file:
        data_file = csv.reader(csv_file)
        if not columns_to_ignore:
            columns_to_ignore = []
        if has_header:
            header = next(data_file)
        data, target = [], []
        # Fix column to ignore ids after removing target_column
        for i, c in enumerate(columns_to_ignore):
            if c > target_column:
                columns_to_ignore[i] -= 1
        for i, d in enumerate(data_file):
            target.append(d.pop(target_column))
            data.append([_d for j, _d in enumerate(d) if j not in columns_to_ignore])
        if categorical_labels:
            assert isinstance(n_classes, int), "n_classes not specified!"
            target = to_categorical(target, n_classes)
        return data, target


class Preloader(object):
    def __init__(self, array, function):
        self.array = array
        self.function = function

    def __getitem__(self, id):
        if type(id) in [list, np.ndarray]:
            return [self.function(self.array[i]) for i in id]
        elif isinstance(id, slice):
            return [self.function(arr) for arr in self.array[id]]
        else:
            return self.function(self.array[id])

    def __len__(self):
        return len(self.array)


class ImagePreloader(Preloader):
    def __init__(self, array, image_shape, normalize=True, grayscale=False):
        fn = lambda x: self.preload(x, image_shape, normalize, grayscale)
        super(ImagePreloader, self).__init__(array, fn)

    def preload(self, path, image_shape, normalize=True, grayscale=False):
        img = load_image(path)
        width, height = img.size
        if width != image_shape[0] or height != image_shape[1]:
            img = resize_image(img, image_shape[0], image_shape[1])
        if grayscale:
            img = convert_color(img, 'L')
        img = pil_to_nparray(img)
        if grayscale:
            img = np.reshape(img, img.shape + (1,))
        if normalize:
            img /= 255.
        return img


class LabelPreloader(Preloader):
    def __init__(self, array, n_class=None, categorical_label=True):
        fn = lambda x: self.preload(x, n_class, categorical_label)
        super(LabelPreloader, self).__init__(array, fn)

    def preload(self, label, n_class, categorical_label):
        if categorical_label:
            #TODO: inspect assert bug
            #assert isinstance(n_class, int)
            return to_categorical([label], n_class)[0]
        else:
            return label


def is_array(X):
    return type(X) in [np.array, np.ndarray, list]


def get_num_features(X):
    if isinstance(X, tf.Tensor):
        return X.get_shape().as_list()[-1]
    elif is_array(X):
        return list(np.shape(X))[-1]
    else:
        raise ValueError("Unknown data type.")


def get_num_classes(Y):
    if is_array(Y):
        # Assume max integer is number of classes
        return np.max(Y) + 1
    elif isinstance(Y, tf.Tensor):
        return ValueError("Cannot automatically retrieve number of classes "
                          "from a Tensor. Please fill 'num_classes' argument.")
    else:
        raise ValueError("Unknown data type.")


def get_num_sample(X):
    if is_array(X):
        return np.shape(X)[0]
    elif isinstance(X, tf.Tensor):
        return X.get_shape()[0]
    else:
        raise ValueError("Unknown data type.")


# ==================
#   STATS UTILS
# ==================

def get_max(X):
    return np.max(X)


def get_mean(X):
    return np.mean(X)


def get_std(X):
    return np.std(X)