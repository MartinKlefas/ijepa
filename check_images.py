import argparse

parser = argparse.ArgumentParser(description="Your script description")
parser.add_argument('--fname', type=str, help="Path to the YAML config file")

args = parser.parse_args()

import yaml, os

with open(args.fname, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

from multiprocessing import Pool, cpu_count
from pathlib import Path

def is_file(path):
    return str(path) if path.is_file() else None

from PIL import Image

def is_image(filename):
    try:
        img = Image.open(filename) # try to open the image file
        img.verify() # verify that it is, in fact an image
        return filename
    except:
        os.unlink(filename)
        return None

if __name__ == '__main__':

    pool = Pool(cpu_count())
        
    try:
        print("Removing non-files")
        all_paths = list(Path(config['data']['image_folder']).glob('**/*.png'))

        files = pool.map(is_file, all_paths)
    finally:
        pool.close()
        pool.join()

    # Remove None values from the list
    files = [f for f in files if f is not None]


    pool = Pool(cpu_count())

    try:
        print("Removing broken images")
        files = pool.map(is_image, files)
    finally:
        pool.close()
        pool.join()
        
    # Remove None values from the list
    files = [f for f in files if f is not None]