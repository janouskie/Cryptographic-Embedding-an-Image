import os
from mat2.mat2 import show_meta, clean_meta
from PIL import Image  # not used directly but just in case
from PIL.ExifTags import TAGS, GPSTAGS

# PATH GOES HERE — 
img_path = "/Users/Administrator2/Downloads/Cryptographic-Embedding-an-Image-main 2/second_photos/p2.jpg"

# intro 
input("press Enter to active the process\n")

print("="*60)
print("1 → see all the metadata information")
print("2 → show just the date/time")
print("3 → Delete")
print("="*60)

while True:
    try:
        pick = int(input("... "))

        if pick == 1:
            print("...")
            show_meta(img_path, True, 1)

        elif pick == 2:
            print("...\n")
            show_meta(img_path, True, 2)

        elif pick == 3:
            print("...")
            clean_meta(img_path, True, True, True, True)

        else:
            print("...")

    except ValueError:
        print("...")
