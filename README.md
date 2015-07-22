# fvbrute

This is my initial attempt at creating a File Vault bruce force program.  It's designed to
brute force the File Vault recovery key against a File Vault encrypted image.  It's specifically
set up to run in conjunction with the libfvde library from here:

https://github.com/libyal/libfvde

This library has to be set up correctly in order for the script to work.

Command Line Arguments:

-o	Offset of image
-e	Path to recovery key
-i	Mount point of encrypted image 
-m	Mount point of decrypted image (where you want the image mounted)
-d	Database name (This is the name of the database that will track the recovery keys used)

Python Module requirements:

os
string
random
argparse
subprocess
sqlite3
