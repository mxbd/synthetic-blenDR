import os
import shutil
import json
import cv2
import os
import numpy as np

def move_images_to_folder(folder_path):
    # create folders for rgb and iseg images
    rgb_folder = os.path.join(folder_path, 'rgb')
    iseg_folder = os.path.join(folder_path, 'iseg')
    os.makedirs(rgb_folder, exist_ok=True)
    os.makedirs(iseg_folder, exist_ok=True)

    # move rgb images to the rgb folder
    for filename in os.listdir(folder_path):
        if filename.startswith('rgb_image_'):
            src_path = os.path.join(folder_path, filename)
            dst_path = os.path.join(rgb_folder, filename)
            shutil.move(src_path, dst_path)

    # move iseg images to the iseg folder
    for filename in os.listdir(folder_path):
        if filename.startswith('iseg_image_'):
            src_path = os.path.join(folder_path, filename)
            dst_path = os.path.join(iseg_folder, filename)
            shutil.move(src_path, dst_path)



def move_labels_to_folder(folder_path):
    # create folder for yolo labels
    yolo_folder = os.path.join(folder_path, 'yolo_labels')
    os.makedirs(yolo_folder, exist_ok=True)

    # move rgb images to the rgb folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            src_path = os.path.join(folder_path, filename)
            dst_path = os.path.join(yolo_folder, filename)
            shutil.move(src_path, dst_path)



def extract_bbox_annots(input_folder, output_folder):

    # define the BGR values for each object
    COLORS = {
    (0, 255, 0): 'akkuhalter',
    (0, 255, 255): 'ausleger',
    (0, 230, 230): 'ausleger',
    (0, 204, 204): 'ausleger',
    (0, 179, 179): 'ausleger',
    (0, 77, 255): 'deckplatte',
    (255, 0, 0): 'grundplatte',
    (153, 26, 255): 'landekufe',
    (153, 51, 255): 'landekufe',
    (255, 255, 0): 'motor',
    (230, 230, 0): 'motor',
    (204, 204, 0): 'motor',
    (179, 179, 0): 'motor',
    (0, 0, 255): 'propeller',
    (0, 0, 230): 'propeller',
    (0, 0, 204): 'propeller',
    (0, 0, 179): 'propeller',
    (26, 77, 128): 'schraube_m6',
    (51, 77, 128): 'schraube_m6',
    (77, 77, 128): 'schraube_m6',
    (102, 77, 128): 'schraube_m6',
    }

    # define YOLO label format
    LABEL_FORMAT = "{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}"

    # define YOLO class IDs
    CLASS_IDS = {
    'akkuhalter': 0,
    'ausleger': 1,
    'deckplatte': 2,
    'grundplatte': 3,
    'landekufe': 4,
    'motor': 5,
    'propeller': 6,
    'schraube_m6': 7
    }

    # loop through each image in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.png'):
            # read the image and convert to BGR format
            image = cv2.imread(os.path.join(input_folder, filename))
            bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # create an empty list to store the YOLO labels
            yolo_labels = []

            # loop through each color and extract the bounding box information
            for color, class_name in COLORS.items():
                mask = cv2.inRange(image, color, color)
                contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
                bounding_boxes = []
                for i, contour in enumerate(contours):
                    # check if the contour is a hole inside another contour
                    if hierarchy[0][i][3] != -1:
                        continue

                    x, y, w, h = cv2.boundingRect(contour)

                    area = w * h
                    if area < 30:
                        continue

                    bounding_boxes.append((x, y, x + w, y + h))

                # combine all bounding boxes of the same color into one
                if bounding_boxes:
                    x_min = min([bb[0] for bb in bounding_boxes])
                    y_min = min([bb[1] for bb in bounding_boxes])
                    x_max = max([bb[2] for bb in bounding_boxes])
                    y_max = max([bb[3] for bb in bounding_boxes])
                    center_x = (x_min + x_max) / (2 * image.shape[1])
                    center_y = (y_min + y_max) / (2 * image.shape[0])
                    width = (x_max - x_min) / image.shape[1]
                    height = (y_max - y_min) / image.shape[0]

                    # create the YOLO label string
                    label = LABEL_FORMAT.format(
                        class_id=CLASS_IDS[class_name],
                        center_x=center_x,
                        center_y=center_y,
                        width=width,
                        height=height
                    )

                    # add the YOLO label to the list
                    yolo_labels.append(label)

            # save the YOLO label file
            label_filename = label_filename = f"rgb_image_{int(os.path.splitext(filename)[0].split('_')[-1]):03d}.txt"
            with open(os.path.join(output_folder, label_filename), 'w') as f:
                f.write('\n'.join(yolo_labels))

