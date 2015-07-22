# This is my attempt at a Apple FileVault Recovery Key brute force tool
# This is designed to be used with the libfvde library from here:
# https://github.com/libyal/libfvde
#
# Licensed under the GPL
# http://www.gnu.org/copyleft/gpl.html
#
# By Tom Yarrish
# Version 1.0

import os
import string
import random
import argparse
from subprocess import Popen
import sqlite3

# This function creates the random 4 character key to be used in the larger key
def fvde_key():
    chars = string.letters.upper() + string.digits
    pwdSize = 4
    key_attempt = ''.join((random.choice(chars)) for x in range(pwdSize))
    return key_attempt

# This function checks the generated key to see if we've seen it before
def check_key(key_select, db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("select * from tracking where enc_key = ( ? );", (key_select,))
    enc_key_exists = c.fetchone()
    if enc_key_exists:
        #print "{} already tried...skipping...".format(key_select) # The key has been tried already move on
        return False
    else:
        print "Adding key {}...".format(key_select) # It's a new key, lets add it to the DB
        c.execute("insert into tracking values(NULL, ? );", (key_select,))
        conn.commit()
        return True

# This is just setting up the different arguments to use for the program
parser = argparse.ArgumentParser()
parser.add_argument('-o', dest='offset', required=True, help='Offset of image (if you use mmls multiply by sector size) to pass to fvdemount')
parser.add_argument('-e', dest='recovery', required=True, help='Path to the recovery key to use')
parser.add_argument('-i', dest='image_loc', required=True, help='Path to the encrypted image mount point')
parser.add_argument('-m', dest='mount_point', required=True, help='Mount point for decrypted image')
parser.add_argument('-d', dest='db_name', required=True, help='Name of database file to track keys')
args = parser.parse_args()

# This just checks if the db file in the command line exists or not
if os.path.isfile(args.db_name):
    print "{} exists...".format(args.db_name)
else:
    conn = sqlite3.connect(args.db_name)
    c = conn.cursor()
    c.execute("create table tracking(id int primary key, enc_key char(29));")

locked = True   # This is just a control for the overall loop

while locked == True:
    decryption_key = "-".join([fvde_key(),fvde_key(),fvde_key(),fvde_key(),fvde_key(),fvde_key()])
    print "Checking decryption key {}...".format(decryption_key)
    already_used_key = check_key(decryption_key, args.db_name)
    if already_used_key:
        print "Trying {} for key...".format(decryption_key)
        # Note depending on where you install libfvde, you may have to change the following line
        proc = Popen(['/usr/local/bin/fvdemount', '-o', args.offset, '-e', args.recovery, '-r', decryption_key, args.image_loc, args.mount_point])
        proc.wait()     # I haven't tested yet that this part is necessary
        if proc.returncode == 0:
            print "We've found the key!  And it is {}".format(decryption_key)
            locked = False
        else:
            print "Not the correct decryption key, retrying..."
    else:
        print "Already tried {}, moving on to the next one...".format(decryption_key)
