
import hashlib
import os

sha256_hash = hashlib.sha256()
f=open("C:/Mani/ML/crewml-dev/crewml/downlaod/2020_apr.csv", 'r')
data=f.read()
sha256_hash.update(data.encode("utf-8"))
print("sig=",sha256_hash.hexdigest())

