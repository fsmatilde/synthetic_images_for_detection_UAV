import splitfolders

dataset_name = 'images'
root_dir = '/mnt/hdd_1_500gb/fsmatilde/PycharmProjects/random_split_files'
dataset_to_split_path = 'dataset_to_split'
output_path = 'output'
random_seed = 18
split_ratio = (1, 0, 0)  # ratio = (train ratio, val ratio, test ratio)

splitfolders.fixed(dataset_to_split_path, output=output_path, seed=random_seed, fixed=split_ratio, move=False)