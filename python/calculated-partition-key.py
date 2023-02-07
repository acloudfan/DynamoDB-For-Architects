# Example of calculated hash
# Splits the catalog across a large number of partitions !!!
# There are many ways to implement this pattern; this is just one way
# Run the code : python python/calculated-partition-key.py 

import hashlib

# Uses the MD5 hashing
def CreateHashedPK(catalog_item_subcategory):
    val = hashlib.md5(catalog_item_subcategory.encode())
    val = val.hexdigest()[0:1]
    
    return val

# generate the PK for computers
pk = "CAT#ELECTRONICS#"+CreateHashedPK("COMPUTERS")
print(pk)

# generate the PK for phone
pk = "CAT#ELECTRONICS#"+CreateHashedPK("PHONE")
print(pk)

# generate the PK for tv
pk = "CAT#ELECTRONICS#"+CreateHashedPK("TV")
print(pk)