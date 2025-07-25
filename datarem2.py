import subprocess

def read_metadata(image_path):
    try:
        # Run exiftool and capture the output
        result = subprocess.run(
            ['exiftool', image_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check if there was an error
        if result.returncode != 0:
            print("Error:", result.stderr)
            return

        # Print metadata
        print("Metadata for:", image_path)
        print(result.stdout)

    except FileNotFoundError:
        print("ExifTool is not installed or not found in PATH.")

# Example usage
if __name__ == "__main__":
    image_file = input("Enter the path to the image file: ")
    read_metadata(image_file)
