import sys

file_path = sys.argv[1]

with open(file_path, "rb") as f:
    data = f.read()
    if 255 in data:
        raise Exception("Error")
    else:
        print(f"File: {file_path}")
        print(f"Size: {len(data)}")