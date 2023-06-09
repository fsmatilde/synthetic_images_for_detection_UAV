import numpy as np
import os
import cv2
from copy import deepcopy
from matplotlib import pyplot as plt
from tqdm import tqdm
from shutil import copy

with open("label_colors.txt", "r") as file:
    label_colors = file.read().split("\n")[:-1]
    label_colors = [x.split("\t") for x in label_colors]
    colors = [x[0] for x in label_colors]
    colors = [x.split(" ") for x in colors]

for i, color in enumerate(colors):
    colors[i] = [int(x) for x in color]

colors = np.array(colors)

annotations_dir = "/mnt/hdd_2TB_2/datasets/training+testing_GAN/inference_img/segmentations"
annotations_files = os.listdir(annotations_dir)
annotations_files = [os.path.join(os.path.realpath("."), annotations_dir, x) for x in annotations_files]

for annotation in tqdm(annotations_files):
    img = cv2.imread(annotation)[:, :, ::-1]

    h, w, _ = img.shape

    img[img > 124] = 255
    img[img < 125] = 0
    modified_annotation = np.zeros((h, w))

    for i, color in enumerate(colors, start=1):
        color = color.reshape(1, 1, -1)
        mask = (color == img)

        r = mask[:, :, 0]
        g = mask[:, :, 1]
        b = mask[:, :, 2]

        mask = np.logical_and(r, g)

        mask = np.logical_and(mask, b).astype(np.int64)

        mask *= i

        modified_annotation += mask

    save_path = annotation.replace(annotations_dir, "output")
    cv2.imwrite(save_path, modified_annotation)