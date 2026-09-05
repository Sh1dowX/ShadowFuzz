# import sys
#
# file_path = sys.argv[1]
#
# with open(file_path, "rb") as f:
#     data = f.read()
#     if len(data) >= 4:
#         if data[0] == 0x41:
#             if data[1] == 0x42:
#                 if data[2] == 0x43:
#                     if data[3] == 0x44:
#                         if b"\xFF\x00\xFF" in data:
#                             raise Exception("CRASH")
#
#     print(f"File: {file_path}")
#     print(f"Size: {len(data)}")
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()

if len(data) > 20:
    raise ValueError("Test crash")

if b"A" in data:
    raise ValueError("A crash")

if b"B" in data:
    raise ValueError("B crash")