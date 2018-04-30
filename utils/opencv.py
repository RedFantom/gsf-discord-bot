"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import os
# Project Modules
from utils.utils import get_temp_directory
# Packages
from PIL import Image
import cv2 as cv
import numpy
from matplotlib import pyplot as plt


def image_to_opencv(image: Image.Image)->numpy.array:
    """Convert a PIL image to a OpenCV compatible array"""
    path = os.path.join(get_temp_directory(), "temp.png")
    image.save(path)
    return cv.imread(path)


def opencv_to_image(arr: numpy.array)->Image.Image:
    """Convert an OpenCV image to a PIL image"""
    return Image.fromarray(cv.cvtColor(arr, cv.COLOR_BGR2RGB))


def feature_match(image: Image.Image, template: Image.Image)->int:
    """Return the amount of features matched with ORB"""
    orb = cv.ORB_create()
    matcher = cv.BFMatcher(cv.NORM_L1, crossCheck=False)
    template = image_to_opencv(template.convert("RGB"))
    tp_kp, tp_ds = orb.detectAndCompute(template, None)
    img = cv.drawKeypoints(template, tp_kp, None, color=(0, 255, 0), flags=0)
    plt.imshow(img)
    plt.show()
    image = image_to_opencv(image.convert("RGB"))
    im_kp, im_ds = orb.detectAndCompute(image, None)
    try:
        matches = matcher.knnMatch(tp_ds, im_ds, k=2)
    except cv.error as e:
        return 0
    result = 0
    for value in matches:
        if len(value) != 2:
            continue
        m, n = value
        if m.distance < 0.8 * n.distance:
            result += 1
    return result
