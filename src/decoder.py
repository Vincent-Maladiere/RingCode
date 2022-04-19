"""
This section is in WIP State.

"""

import cv2
import numpy as np
from matplotlib import pyplot as plt


def encoder(module_size_pixels, min_radius, max_radius):
    """
    Draw modules as circles section, beginning with the outside,
    and then adding co-centric, smaller circles recursively.
    """
    current_radius = max_radius
    while current_radius >= min_radius:
        for angle in angles:
            if black:
                cv2.drawCircleSegment(angle, current_radius, black)
        cv2.drawCircle(current_radius - module_size_pixels, white)
        current_radius -= module_size_pixels


def barcode_recognition(img_binary):
    """
    Locate a ring-shaped barcode in an image and to estimate its centroid.

    OpenCV provides the class SimpleBlobDetector.
    It allows filtering the blobs by area, circularity, inertia, convexity
    and colour

    - Due to distorsion, the central circular blob is referred to as ellipse.
    - The centre of the barcode is white.


    """
    cv2.SimpleBlobDetector(img_binary)
    return centroid, major_axis_length, minor_axis_length


def add_keypoints(img, keypoints):
    print(keypoints)
    img_with_keypoints = img.copy()
    for k in keypoints:
        cv2.circle(
            img_with_keypoints,
            (int(k.pt[0]), int(k.pt[1])),
            radius=int(k.size / 2),
            color=(0, 0, 255),
            thickness=5,
        )
    return img_with_keypoints


def barcode_recognition(img):
    """
    TODO:

    - speed things up
    - access the blob’s moments to determine the length of both the ellipse’s major and minor axis

    https://stackoverflow.com/questions/13534723/how-to-get-extra-information-of-blobs-with-simpleblobdetector/25152785#25152785
    """

    H, W, _ = img.shape
    avg_dimension = (W + H) / 2
    r_min = avg_dimension / 16
    r_max = avg_dimension / 4
    min_area = np.pi * r_min ** 2
    max_area = np.pi * r_max ** 2

    params = cv2.SimpleBlobDetector_Params()

    params.filterByColor = True
    params.blobColor = 255
    params.filterByArea = True
    params.minArea = min_area
    params.maxArea = max_area

    params.filterByCircularity = True
    params.minCircularity = 0.8
    params.maxCircularity = 1

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(img)

    img_with_keypoints = add_keypoints(img, keypoints)
    # img_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    plt.figure(figsize=(8, 8))
    plt.imshow(img_with_keypoints)

    return keypoints
