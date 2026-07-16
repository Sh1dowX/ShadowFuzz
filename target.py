import sys
import time

file_path = sys.argv[1]
time.sleep(5)

with open(file_path, "rb") as f:
    data = f.read()
    if b"\xff\x00\xff" in data:
        raise Exception("Error")
    else:
        print(f"File: {file_path}")
        print(f"Size: {len(data)}")