import os
import hashlib

sha256 = hashlib.sha256()

with open(f"./rendered_configs/lab-rtr01.cfg", 'rb') as file:
    data = file.read()
    sha256.update(data)

print(sha256.hexdigest())

