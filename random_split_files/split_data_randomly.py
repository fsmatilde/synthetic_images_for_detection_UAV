import splitfolders
from pycocotools.coco import COCO
import requests
import os
from tqdm import tqdm
import json


class data_split:
    """
    Downloads splited images and filters jsons
    to only keep annotations of this images
    """

    def __init__(self, json_path, imgs_dir, categ='boat'):
        self.coco = COCO(json_path)  # instanciate coco class
        self.json_path = json_path
        self.imgs_dir = imgs_dir
        self.categ = categ
        self.images = self.get_imgs_from_json()

    def get_imgs_from_json(self):
        """returns the image names present in json original file"""
        # instantiate COCO specifying the annotations json path
        # Specify a list of category names of interest
        catIds = self.coco.getCatIds(catNms=[self.categ])
        print("catIds: ", catIds)
        # Get the corresponding image ids and images using loadImgs
        imgIds = self.coco.getImgIds(catIds=catIds)
        images = self.coco.loadImgs(imgIds)
        print(f"{len(images)} images in '{self.json_path}' with '{self.categ}' instances")
        self.catIds = catIds  # list
        return images

    def filter_json_by_file_name(self, new_json_path, dataset_name):
        """creates a new json with the desired image annotations"""
        ### Filter images:
        print("Filtering the annotations ... ")
        json_parent = os.path.split(new_json_path)[0]
        os.makedirs(json_parent, exist_ok=True)
        folder_list = ['train']          # 'train', 'test' or 'val'
        files_list = []
        for folder in folder_list:
            files_list += os.listdir(json_parent + '/' + folder + '/' + dataset_name)
        sorted(files_list)
        imgs_ids = [x['id'] for x in self.images if x['file_name'] in files_list]  # get img_ids of files_list
        new_imgs = [x for x in self.coco.dataset['images'] if x['id'] in imgs_ids]
        ### Filter annotations
        new_annots = [x for x in self.coco.dataset['annotations'] if x['image_id'] in imgs_ids]
        ### Reorganize the ids
        new_images, new_annotations = self.modify_ids(new_imgs, new_annots)
        ### Filter categories
        print("filtered_images: " + str(len(imgs_ids)))
        data = {
            "info": self.coco.dataset['info'],
            "licenses": self.coco.dataset['licenses'],
            "images": new_images,
            "annotations": new_annotations,
            "categories": self.coco.dataset['categories']
        }
        print("saving json: ")
        with open(new_json_path, 'w') as f:
            json.dump(data, f)

    # def modify_files_name(self, new_json_path):
    #     print("Renaming the annotations ... ")
    #     json_parent = os.path.split(new_json_path)[0]
    #     os.makedirs(json_parent, exist_ok=True)
    #     for image in self.coco.dataset['images']:
    #         image['file_name'] = image['file_name'][:-4] + '_GAN' + '.jpg'
    #     data = {
    #         "info": self.coco.dataset['info'],
    #         "licenses": self.coco.dataset['licenses'],
    #         "images": self.coco.dataset['images'],
    #         "annotations": self.coco.dataset['annotations'],
    #         "categories": self.coco.dataset['categories']
    #     }
    #     print("saving json: ")
    #     with open(new_json_path, 'w') as f:
    #         json.dump(data, f)

    def modify_ids(self, images, annotations):
        """
        creates new ids for the images. I.e., reorganizes the ids and returns the dictionaries back
        images: list of images dictionaries
        imId_counter: image id starting from one (each dicto will start with id of last json +1)
        """
        print("Reinitialicing images and annotation IDs ...")
        ### Images
        old_new_imgs_ids = {}  # necessary for the annotations!
        for n, im in enumerate(images):
            old_new_imgs_ids[images[n]['id']] = n + 1  # dicto with old im_ids and new im_ids
            images[n]['id'] = n + 1  # reorganize the ids
        ### Annotations
        for n, ann in enumerate(annotations):
            annotations[n]['id'] = n + 1
            old_image_id = annotations[n]['image_id']
            annotations[n]['image_id'] = old_new_imgs_ids[old_image_id]  # replace im_ids in the annotations as well
        return images, annotations

    def save_imgs(self):
        """saves the desired images"""
        print("Saving the images with required categories ...")
        os.makedirs(self.imgs_dir, exist_ok=True)
        # Save the images into a local folder
        for im in tqdm(self.images):
            img_data = requests.get(im['coco_url']).content
            with open(os.path.join(self.imgs_dir, im['file_name']), 'wb') as handler:
                handler.write(img_data)


def main(dataset_to_split_path, output_path, random_seed, split_ratio, root_dir, dataset_name, category='boat'):
    json_file = root_dir + '/' + json_to_filter
    imgs_dir = root_dir + '/' + dataset_to_split_path
    new_json_path = root_dir + '/' + output_path + '/' + 'new.json'
    # # splitfolders.ratio(dataset_to_split_path, output=output_path, seed=random_seed, ratio=split_ratio)
    splitfolders.fixed(dataset_to_split_path, output=output_path, seed=random_seed, fixed=split_ratio, move=False)
    random_data_split = data_split(json_file, imgs_dir, categ=category)
    # # random_data_split.save_imgs()
    random_data_split.filter_json_by_file_name(new_json_path, dataset_name)
    # random_data_split.modify_files_name(new_json_path)
if __name__ == '__main__':
    dataset_name = 'images'
    root_dir = '/mnt/hdd_1_500gb/fsmatilde/PycharmProjects/random_split_files'
    dataset_to_split_path = 'dataset_to_split'
    json_to_filter = 'annotations.json'
    output_path = 'output'
    random_seed = 33
    split_ratio = (78, 0, 0)  # ratio = (train ratio, val ratio, test ratio)
    main(dataset_to_split_path, output_path, random_seed, split_ratio, root_dir, dataset_name, category='boat')