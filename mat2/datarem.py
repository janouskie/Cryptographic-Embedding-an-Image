import os 
from mat2 import *
# from libmat2 import _get_member_meta  
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


# show_meta("photos/testsubject3.jpg", True)
file_location = "/media/sf_Phone_Link/p2.jpg"

input("Hello! Please press enter to begin the metadata removal / inclusion process \n")

# print (user_choice)
print('==============================================================')
print ('Enter 1 to display the metadata of the given file \n')
print ('Enter 2 to list out the date and time of the file \n')
print ('Enter 3 to remove the metadata found in this file\n')

while True:
    try:
        choice = int(input('Enter your choice: '))

        if (choice == 1):
            # print("choice no.1")
            print("Loading...")
            show_meta(file_location,True, 1)

        elif (choice == 2):
            print(" Loading... \n")
            show_meta(file_location,True, 2)

        elif (choice == 3):
            print("Removing the metadata of the given file...")
            clean_meta(file_location,True,True,True,True)
        else:
            print('Invalid choice!')

    except ValueError:
        print ("Invalid input!")



