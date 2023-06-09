from segments import SegmentsClient, SegmentsDataset
from segments.utils import export_dataset
import os


# image_folder = r'/mnt/hdd_2TB_2/datasets/test_seagull/images'
# files_list = sorted(os.listdir(image_folder))
# image_files = [os.path.join(os.path.realpath('.'),image_folder,x) for x in files_list]

api_key = "3ec98b783b2b2e3c7d85828c5b532f411bf4b2dd"
# api_key = "aaa82c420efb74dfdb73f6848dac7598d2af0cc2"
client = SegmentsClient(api_key)


# for i, image in enumerate(image_files[61:]):
#
#     with open(f"{image}", "rb") as f:
#         asset = client.upload_asset(f, filename=files_list[i])
#
#     image_url = asset.url
#     dataset = "fsmatilde/Seagull"
#     name = files_list[i]
#     attributes = {"image": {"url": image_url}}
#     sample = client.add_sample(dataset, name, attributes)
#     print(str(i) + '/' + str(len(files_list)))

dataset_identifier = "fsantos98/Seagull_instance"
name = "Seagull_instance_test_2"

#client.add_release(dataset_identifier, name)
release = client.get_release(dataset_identifier, name)

# dataset = SegmentsDataset(release, labelset='ground-truth', filter_by=['labeled', 'reviewed'])
dataset = SegmentsDataset(release, filter_by=['labeled', 'reviewed'])

export_dataset(dataset, export_format='coco-instance')
