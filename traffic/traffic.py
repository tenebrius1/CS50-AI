import cv2 as cv
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test, y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    # * Initializes list of images and list of labels
    imgs, labels = list(), list()

    # * Gets a list of all the subdirectories in data_dir
    subdirs = os.listdir(data_dir)

    # * Loops trhough each subdirectory
    for subdir in subdirs:

        # * Gets the path of the subdir and gets a list of all the images files in that specific subdirectory
        subdir_path = f"{data_dir}\\{subdir}"
        images = os.listdir(subdir_path)

        # * Loops through all images in the subdirectory
        for image in images:
            # * Gets the absolute path of the image
            img_path = os.path.join(os.path.abspath(data_dir), subdir, image)
            # * Using cv2, reads the image into a numpy ndarray datatype
            img = cv.imread(img_path)
            # * Resizes the image to the correct height and width
            img = cv.resize(img, dsize=(IMG_HEIGHT, IMG_WIDTH))

            # * Adds the image array and label into their respective list
            imgs.append(img)
            labels.append(int(subdir))

    return (imgs, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    from tensorflow.keras import layers

    # * Create a convolutional neural network
    model = tf.keras.Sequential(
        [
            # * Convolutional layer. Learns 32 filter using a 3x3 kernel
            layers.Conv2D(
                32, (3, 3), activation="relu", input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)
            ),
            # * Max pooling layer, using 2x2 size
            layers.MaxPooling2D((2, 2)),
            # * 2nd convolutional and pooling layer
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            # # * Flatten units
            layers.Flatten(),
            # * Adds hidden layer with dropout of 20%
            layers.Dense(128, activation="relu"),
            layers.Dense(64, activation="relu"),
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.5),
            # * Adds an output layer with output units for all of the different traffic signs
            layers.Dense(3, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
