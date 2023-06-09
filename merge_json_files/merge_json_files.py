from pycocotools.coco import COCO
import json

annotations_1 = '/mnt/hdd_1_500gb/fsmatilde/PycharmProjects/image-to-coco-json-converter/json_files_to_merge/merged_annotations.json'
annotations_2 = '/mnt/hdd_1_500gb/fsmatilde/PycharmProjects/image-to-coco-json-converter/json_files_to_merge/annotations_blender_625.json'
output_file = '/mnt/hdd_1_500gb/fsmatilde/PycharmProjects/image-to-coco-json-converter/output/merged_annotations.json'

# Standard COCO format
coco_format = {
    "info": {},
    "licenses": [],
    "images": [{}],
    "categories": [{}],
    "annotations": [{}]
}

coco1=COCO(annotations_1)
coco2=COCO(annotations_2)

coco_format["info"] = coco1.dataset['info']
coco_format["licenses"] = coco1.dataset['licenses']
coco_format["categories"] = coco1.dataset['categories']

image_list = coco1.dataset['images']
annotation_list = coco1.dataset['annotations']

last_image_id = coco1.dataset['images'][-1]['id']
last_annotation_id = coco1.dataset['annotations'][-1]['id']

for image in coco2.dataset['images']:
    old_image_id = image['id']
    new_image_id = last_image_id + 1
    image['id'] = new_image_id
    image_list.append(image)
    for annotation in coco2.dataset['annotations']:
        if annotation['image_id'] == old_image_id:
            annotation['image_id'] = new_image_id
            new_annotation_id = last_annotation_id + 1
            annotation['id'] = new_annotation_id
            annotation_list.append(annotation)
            coco2.dataset['annotations'].remove(annotation)
            last_annotation_id += 1
    last_image_id += 1
    print(len(coco2.dataset['images'])-old_image_id)

coco_format["images"] = image_list
coco_format["annotations"] = annotation_list

with open(output_file, "w") as outfile:
    json.dump(coco_format, outfile)