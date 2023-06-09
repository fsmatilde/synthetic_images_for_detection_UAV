import os
import cv2
from PIL import Image

input_folder = r'/mnt/hdd_2TB_2/datasets/blender_625/images'
output_folder = r'/mnt/hdd_2TB_2/datasets/blender_625/images_png'

files_list = sorted(os.listdir(input_folder))
image_files = [os.path.join(os.path.realpath('.'),input_folder,x) for x in files_list]

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for counter, image in enumerate(image_files[:]):
    old_img = Image.open(image)
    new_img = old_img.convert('RGB')
    new_img.save(output_folder + '/' + files_list[counter][:-3] + 'jpg')
    print(str(counter+1)+'/'+str(len(files_list)))


    # img = cv2.imread(image)[:, :, ::-1]
    # img[img > 3] = 255
    # cv2.imwrite(image, img)

