import cv2
import numpy as np
from sklearn.linear_model import LinearRegression
def enhanced_color(original_image):
    original_image_float = original_image.astype(np.float32)
    red_channel = original_image_float[:, :, 0].ravel()
    green_channel = original_image_float[:, :, 1].ravel()
    blue_channel = original_image_float[:, :, 2].ravel()
    X = np.stack([red_channel, green_channel], axis=1)
    regressor = LinearRegression()
    regressor.fit(X, blue_channel.reshape(-1, 1))
    predicted_blue_channel = regressor.predict(X)
    predicted_blue_channel = predicted_blue_channel.reshape(original_image.shape[:2])
    balanced_image = original_image.copy()
    balanced_image[:, :, 2] = predicted_blue_channel
    balanced_image = np.clip(balanced_image, 0, 255).astype(np.uint8)
    return balanced_image

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA, keep_aspect_ratio = False):
    if keep_aspect_ratio == False:
        return cv2.resize(image, (width, height))
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def enhanced_image_color(image):
    # Convert the image from BGR to HSV color space
    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # Adjust the hue, saturation, and value of the image
    # Adjusts the hue by multiplying it by 0.7
    image[:, :, 0] = image[:, :, 0] * 0.7
    # Adjusts the saturation by multiplying it by 1.5
    image[:, :, 1] = image[:, :, 1] * 1.5
    # Adjusts the value by multiplying it by 0.5
    image[:, :, 2] = image[:, :, 2] * 0.5

    # Convert the image back to BGR color space
    enhanced_image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)

    return enhanced_image

def enhanced_image_sharpness(image):

    # Create the sharpening kernel
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    # Sharpen the image
    enhanced_image = cv2.filter2D(image, -1, kernel)

    return enhanced_image

def enhanced_image_decrease_noise(image):
    enhanced_image = cv2.medianBlur(image, 11)
    return enhanced_image