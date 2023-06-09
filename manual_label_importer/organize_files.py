import os
import shutil

image_folder = r'/mnt/hdd_1_500gb/fsmatilde/PycharmProjects/manual_labelling/segments/fsmatilde_Seagull/Seagull_v1.3'
annotations_folder = '/mnt/hdd_2TB_2/datasets/test_seagull_2/annotations/masks'
files_list = sorted(os.listdir(image_folder))
image_files = [os.path.join(os.path.realpath('.'),image_folder,x) for x in files_list]

for i, image in enumerate(image_files[:]):
    if image[-16:] == 'ground-truth.png':
        os.remove(image)
    elif 'coco-panoptic' in image:
        shutil.move(image, annotations_folder)
    else:
        print(str(i)+'/'+str(len(image_files)))