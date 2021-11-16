import re
import urllib.request
import pathlib
import datetime
import codecs
import io
import os
import sys
import platform
import getpass

# csv input format:
#   "word";
#   "meaning";
#   "<img src='https://contentcdn.lingualeo.com/uploads/picture/12345.png'>";
#   "transcription";
#   "example";
#   "[sound:https://audiocdn.lingualeo.com/v2/1/12345.mp3]";
#   ;
#   ;
# " label"

# out format (separated with \t)
# "word"	"meaning"	"12345.png"	"transcription"	"example"	[sound:word_date_time.mp3]			"label"


def getStoragePath():
    curOS = platform.system()
    user = getpass.getuser()
    prefix = ''
    ankiPath = ''
    ankiUser = ''

    if curOS == 'Linux':
        prefix = '/home'
        ankiUser = 'User 1'
        ankiPath = '.local/share/Anki2/'
    else:
        raise ValueError('Unsupported OS')

    return prefix + '/' + user + '/' + ankiPath + '/' + ankiUser + '/collection.media/'

# download a file
def download(link, name):
    urllib.request.urlretrieve(link, anki_path + name)

# extract the link
def get_link(line):
    m = re.search(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*", line)
    if m != None:
        return m.group(0)
    return None

# get the file extension
def get_extention(line):
    res = None
    pos = line.rfind(".")
    if pos > 0:
        res = line[pos + 1:]
    return res

# download an image file
def download_image(prefix, postfix, line):
    res = None
    link = get_link(line)
    if link != None:
        ext = get_extention(link)
        name = prefix + "_" + postfix + "." + ext
        download(link, name)

        res = "\"" + name + "\""
    return res

# download a sound file
def download_sound(prefix, postfix, line):
    res = None
    link = get_link(line)
    if link != None:
        ext = get_extention(link)
        name = prefix + "_" + postfix + "." + ext
        #print(name)
        download(link, name)
        res = "[sound:" + name + "]"

    return res


# fin = "lingualeo.csv"

# input file
fin = None
# out file
fout = "export.txt"
# input content
content = []
# media path
anki_path = getStoragePath()
dt = datetime.datetime.now().strftime("%y%m%d_%H%M")
counter = 1

str_press_any_key = "\nPress anykey to continue..."

# try to get the input file name
try:
    fin = sys.argv[1]
except IndexError:
    input("No input file." + str_press_any_key)
    sys.exit(1)

# Check if path exits
if os.path.exists(fin) == False:
    input("The input file does not exist." + str_press_any_key)
    sys.exit(1)

# get the file content
with io.open(fin, encoding='utf-8') as f:
    for line in f:
        content.append(line)

# handle and save
with open(fout, 'w', encoding='utf-8') as f:
    for line in content:
        #print(line)
        #line = content[0]
        #continue
        fields = line.split(";")
        word = fields[0].replace('"', "")
        image = download_image(word, dt, fields[2])
        sound = download_sound(word, dt, fields[5])

        print("{0} {1} i={2},\ts={3}".format(str(counter).ljust(3), word.ljust(20), image != None, sound != None))
        counter += 1

        summary = ""
        for i in range(0, len(fields)):
            if summary != "":
                summary += "\t"
            # tab_2 = image, update it
            # tab_5 = sound, update it
            # skip tabs 6 and 7 and, 8 is label
            if i == 2:
                if image != None:
                    summary += image
            elif i == 5:
                if sound != None:
                    summary += sound
            elif i != 6 and i != 7:
                summary += fields[i]

        f.write(summary)
    # finish
    print(str(counter) + " entries handled and stored at " + anki_path)
    f.close()

input("Done." + str_press_any_key)
