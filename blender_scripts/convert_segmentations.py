# this script converts segmentations into a binary format where 255 is the object of interest
# and 0 is the 'dont care label'
import os
from tqdm import tqdm
import cv2

annotations_dir = '/mnt/hdd_2tb_1/fsmatilde/Dataset_Blender/Final+no_sequence_division+no_impossible_sequences/segmentations_only_boat'

files_list = sorted(os.listdir(annotations_dir))
annotations_files = [os.path.join(os.path.realpath('.'), annotations_dir, x) for x in files_list]

for annotation in tqdm(annotations_files):
    img = cv2.imread(annotation)[:, :, ::-1]
    img[img == 100] = 0
    img[img > 200] = 255
    cv2.imwrite(annotation, img)
