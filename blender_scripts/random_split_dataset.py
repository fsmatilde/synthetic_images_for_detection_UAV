import splitfolders
import os
import shutil

images_dir = '/mnt/hdd_2tb_1/fsmatilde/Dataset_Blender/Final+no_sequence_division+no_impossible_sequences/images'
segmentations_dir = '/mnt/hdd_2tb_1/fsmatilde/Dataset_Blender/Final+no_sequence_division+no_impossible_sequences/segmentations_only_boat'
output_folder = 'blender_625'
total_filtered_images = 16
seed_number = 51

# Randomly filter dataset and save those images in the output folder
splitfolders.fixed(images_dir, output=output_folder, seed=seed_number, fixed=(total_filtered_images, 0, 0))

# Read images name and create a second folder with the respective segmentations
image_list = os.listdir(output_folder+'/train/images')

if not os.path.exists(output_folder + '/segmentations'):
    os.makedirs(output_folder + '/segmentations')

for image_name in image_list:
    copy = segmentations_dir + '/' + image_name
    paste = output_folder + '/segmentations/' + image_name
    shutil.copy(copy, paste)
    print(image_name)
