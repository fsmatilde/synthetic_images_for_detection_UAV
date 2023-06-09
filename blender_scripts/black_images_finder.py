import os
import cv2

segmentations_folder = '/mnt/hdd_2tb_1/fsmatilde/Scripts/blender_625/segmentations'
images_folder = '/mnt/hdd_2tb_1/fsmatilde/Scripts/blender_625/train/images'

files_list = sorted(os.listdir(segmentations_folder))
segmentation_files = [os.path.join(os.path.realpath('.'), segmentations_folder, x) for x in files_list]

image_counter = 0
delete_list = []

for i, image in enumerate(segmentation_files[:]):
    img = cv2.imread(image)[:, :, ::-1]
    # Verify if there is any object of interest in the image
    if img.sum() == 0:
        image_counter += 1
        delete_list.append(files_list[i])
        os.remove(image)
    print(str(i + 1) + '/' + str(len(files_list)) + ' ' + str(image))

for images in delete_list:
    os.remove(images_folder + '/' + images)

print(str(image_counter) + ' black images in ' + str(i+1) + ' total images')