import os 
from mat2 import *
# from libmat2 import _get_member_meta  
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

# ####################################################
# @staticmethod
# def _get_member_meta(member: ArchiveMember) -> Dict[str, str]:
#     assert isinstance(member, tarfile.TarInfo)  # please mypy
#     metadata = {}
#     if member.mtime != 0:
#         metadata['mtime'] = str(datetime.datetime.fromtimestamp(member.mtime))
#     if member.uid != 0:
#         metadata['uid'] = str(member.uid)
#     if member.gid != 0:
#         metadata['gid'] = str(member.gid)
#     if member.uname != '':
#         metadata['uname'] = member.uname
#     if member.gname != '':
#         metadata['gname'] = member.gname
#     return metadata

# ####################################################

# show_meta("photos/testsubject3.jpg", True)
file_location = "photos/content.jpg"

input("Hello! Please press enter to begin the metadata removal / inclusion process ")

# print (user_choice)

print ('Enter 1 for choice 1\n')
print ('Enter 2 for choice 2\n')
print ('Enter 3 for choice 3\n')

try:
    choice = int(input('Enter your choice: '))

    if (choice == 1):
        # print("choice no.1")
        print("The date and time are as listed: ")
        show_meta(file_location,True, 1)

    elif (choice == 2):
        print("The original ID of the photo is as listed below: ")
        show_meta(file_location,True, 2)
    elif (choice == 3):
        print("The date and time are as listed: ")
        show_meta(file_location,True, 1)
    else:
        print('Invalid choice!')

except ValueError:
    print ("Invalid input!")

    
# while True:
#     print (user_choice)

#     try :
#         option = user_choice 
#         if option == 1:
#             print("The date and time are as listed:")
#             with open (file_location) as fp:
#                 for line_num, line in enumerate(fp):
#                     if 'DateTime' in line:
#                         print ("", line) 

#     except: 
#         print ("Sorry!") 

