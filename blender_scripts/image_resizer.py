from PIL import Image
import os
import cv2

input_folder = '/mnt/hdd_2tb_1/fsmatilde/Dataset_Blender/625_550x550/segmentations'
output_folder = '/mnt/hdd_2tb_1/fsmatilde/Dataset_Blender/625_550x550/segmentations_550x550'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# New dimensions
new_width = 978
new_height = 550

files_list = sorted(os.listdir(input_folder))
image_files = [os.path.join(os.path.realpath('.'), input_folder, x) for x in files_list]

counter = 0
nil_counter = 0
nil_list =[]
for image in image_files[:]:
    # Open the image
    img = Image.open(image)

    # Resize image
    img = img.resize((new_width, new_height))
    # Crop image
    crop_width = 550
    left = (new_width - crop_width) // 2
    right = left + crop_width
    img = img.crop((left, 0, right, new_height))

    # Save image
    img.save(output_folder + '/' + files_list[counter])

    output_img = cv2.imread(output_folder + '/' + files_list[counter])[:, :, ::-1]

    # Adjust pixel color because of downsize damages, uncomment to apply in segmentations
    output_img[output_img > 0] = 255
    cv2.imwrite(output_folder + '/' + files_list[counter], output_img)

    print(str(counter+1) + '/' + str(len(files_list)) + ' ' + str(image))
    counter += 1
