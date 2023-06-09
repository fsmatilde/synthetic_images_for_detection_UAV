import numpy as np
from pycocotools.coco import COCO
import os
from matplotlib import image as img
from pathlib import Path


annFile = "/mnt/hdd_1_500gb/fsmatilde/PycharmProjects/json-to-mask-converter/annotations/annotations_real_10k.json"
output_dir = "/mnt/hdd_1_500gb/fsmatilde/PycharmProjects/json-to-mask-converter/output"
total_images = 10000
image_height = 550
image_width = 550

coco=COCO(annFile)

# Get category IDs and annotation IDs
catIds = coco.getCatIds()
annsIds = coco.getAnnIds()

# Create folders named after annotation categories
for cat in catIds:
    Path(os.path.join(output_dir,coco.loadCats(cat)[0]['name'])).mkdir(parents=True, exist_ok=True)

for image in range(9999,total_images+1):
    boat_list = []
    for annotation in annsIds:
        if coco.loadAnns(annotation)[0]['image_id']==image:
            boat_list.append(annotation)

    # Get individual masks
    final_mask = np.zeros((image_height,image_width), dtype=np.int8)
    for boat in boat_list:
        boat_mask = coco.annToMask(coco.loadAnns(boat)[0])
        final_mask = np.add(final_mask, boat_mask)
    final_mask[final_mask > 1] = 1
    # Save masks to BW images
    file_path = os.path.join(output_dir,coco.loadCats(coco.loadAnns(boat_list[0])[0]['category_id'])[0]['name'],coco.loadImgs(coco.loadAnns(boat_list[0])[0]['image_id'])[0]['file_name'])
    img.imsave(file_path, final_mask, cmap="gray")

    print(str(image)+'/'+str(total_images)+' working on '+coco.loadImgs(coco.loadAnns(boat_list[0])[0]['image_id'])[0]['file_name'])