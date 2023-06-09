# Script to create a new folder with the filtered dataset and renamed files
import shutil
import os


original_folder = '/mnt/hdd_2tb_1/fsmatilde/Dataset_Blender/Final+sequence_divided+impossible_sequences'
new_folder = '/mnt/hdd_2tb_1/fsmatilde/Dataset_Blender/Final+no_sequence_division+no_impossible_sequences'
work_mode = ['Segmentations']          #'Images' or 'Segmentations'

for mode in work_mode:
    image_counter = 1
    output_path = new_folder + '/' + mode
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for i in range(1, 13825):
        sequence = '/Sequence.' + format(i, '04')
        if i not in range(9505, 10369) and i not in range(11233, 12097):    # impossible sequences
            if not os.path.exists(original_folder + sequence):
                print('Sequence ' + str(i) + ' doesnt exist')
            else:
                print('Working on ' + mode + ' of the sequence ' + str(i))
                for n in range(0, 13):
                    image = '/' + mode[:-1] + format(1 + 20 * n, '04') + '.png'
                    old_image = original_folder + sequence + '/' + mode + image
                    new_image = output_path + '/Image' + format(image_counter, '06') + '.png'
                    shutil.copy(old_image, new_image)
                    image_counter += 1
