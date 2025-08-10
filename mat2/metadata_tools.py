import os
from PIL import Image
from PIL.ExifTags import TAGS


# gets the metadata of a uploaded file
def grab_all_metadata(pic_path):
    if not os.path.exists(pic_path):
        return "The file doesn’t even exist"

    try:
        img = Image.open(pic_path)
        metadata = img._getexif()

        # if theres nothing in there
        if not metadata:
            return "no metadata in here "

        lines = []
        for the_tag in sorted(metadata.keys()):
            tag_name = TAGS.get(the_tag, the_tag)
            val = metadata[the_tag]

            # if it has value 
            if isinstance(val, bytes):
                val = f"<binary stuff… {len(val)} bytes>"

            lines.append(f"{tag_name}: {val}")

        lines.append("-" * 40 + " deleting the metadata") 
        return "\n".join(lines)

    except Exception as e:
        # just for error handling to know what happened"
        return f"error has occured: {e}"


# this one’s only for when/where the pic was taken (or whatever date stuff is there)
def only_the_dates(pic_path):
    if not os.path.exists(pic_path):
        return "missing file? "

    try:
        im = Image.open(pic_path)
        exif_data = im._getexif()

        if not exif_data:
            return "no metadata found"

        dates_found = []
        for tag, val in exif_data.items():
            name = TAGS.get(tag, tag)
            if "Date" in str(name) or "Time" in str(name):
                dates_found.append(f"{name}: {val}")

        if not dates_found:
            return "no dates found"

        return "\n".join(dates_found)

    except Exception as err:
        return f"error has occured {err}"


# gonna make a version of the image without metadata — just pixels
def wipe_meta_keep_pixels(pic_path):
    if not os.path.exists(pic_path):
        return "no file exists"

    try:
        old = Image.open(pic_path)
        new_pic = Image.new(old.mode, old.size)
        new_pic.putdata(list(old.getdata()))

        name, ext = os.path.splitext(pic_path)
        clean_version = f"{name}_clean{ext}"

        new_pic.save(clean_version)

        return f"file been wiped {clean_version}"

    except Exception as crash:
        return f"error has occured: {crash}"


# Aliases for compatibility with other modules
display_metadata = grab_all_metadata
display_datetime = only_the_dates
remove_metadata = wipe_meta_keep_pixels

if __name__ == '__main__':
    app.run(debug=True, port=8080)
