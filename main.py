#!/usr/bin/env python
# encoding=utf8  

# imports
from slugify import slugify
# from unidecode import unidecode
import fnmatch
import os
import argparse
import re
import json
import php
import sys
import unicodedata

# header of file to get args
parser = argparse.ArgumentParser(description='Create translator files for laravel.')
parser.add_argument('from_path', metavar='from_path', type=str, help='Path where it will find the files')
parser.add_argument('prefix', metavar='prefix', type=str, help='the prefix of translator function')
parser.add_argument('destiny', metavar='destiny', type=str, help='the destiny file')
args = parser.parse_args()

# main scope
main_exp = re.compile(r'<(?!(?:script)|(?:img)|(?:input))[a-z0-9]+[^>]*>([^<>]+)<\/[a-z0-9]+>')
not_exp = re.compile('(@[a-z-A-Z0-9]+(\((.)*\))?)|({{.*}})')

reload(sys)  
sys.setdefaultencoding('utf8')

try:
    to_file = open(args.destiny + '.map', 'r')
    mapper = json.loads(to_file.read())
    to_file.close()
except ValueError and IOError:
    mapper = {}


# functions
def add_to_mapper(mainmapper, mylist, value):
    key = mylist[0]
    try:
        if type(mainmapper[key]) is dict and not len(mylist) == 1:
            add_to_mapper(mainmapper[key], mylist[1:], value)
        else:
            mainmapper[key] = value
    except KeyError:
        mainmapper[key] = create_map_from_list(mylist[1:], value)


def create_map_from_list(mylist, value):
    if len(mylist) == 0:
        return value
    else:
        key = mylist[0]
        return {key: create_map_from_list(mylist[1:], value)}


# Find files
matches = []
for root, dirnames, filenames in os.walk(args.from_path):
    for filename in fnmatch.filter(filenames, '*.blade.php'):
        matches.append(os.path.join(root, filename))

file_count = 0

# Find Strings
for filename in matches:
    file_count += 1

    file = open(filename, 'r')
    matches_count = 0

    filemapper = {}

    try:
        file_content = file.read().decode("utf-8")
        file.close()
        search = main_exp.findall(file_content)
        for row in search:
            row = row.replace("\n", " ").strip()
            if not not_exp.match(row) and len(row) > 3:
                matches_count += 1

                keys = row.split(' ')
                keys = list(filter(lambda word: len(word.replace('-', '').replace('*', '').strip()) > 0, keys))
                keys = keys[:6]
                keys = list(map(unicode, keys))
                keys = list(map(slugify, keys))

                filemapper['-'.join(keys)] = row

    except AttributeError as e:
        print('File ' + filename + ' ERROR: ' + str(e))
        continue
    except UnicodeError as e:
        print('File ' + filename + ' ERROR: ' + str(e))
        continue
    except TypeError as e:
        print('File ' + filename + ' ERROR: ' + str(e))
        continue

    mapperPath = filename.replace(args.from_path, '').replace('.blade.php', '').replace('/', '\\').strip()
    if mapperPath[0] == '\\':
        mapperPath = mapperPath[1:]

    mapperPath = mapperPath.split('\\')
    mapperPath = list(map(unicode, mapperPath))
    mapperPath = list(map(slugify, mapperPath))

    add_to_mapper(mapper, mapperPath, filemapper)

    if file_count > 0:
        try:
            file = open(filename + '.bak', 'w+')
            file.write(file_content)
            file.close()
        except UnicodeError as e:
            print(e)

        prefix = args.prefix + '.'.join(mapperPath)
        for key in filemapper:
            try:
                laravel_code = "{{ trans('" + prefix + "." + key + "') }}"
                file_content = file_content.replace(filemapper[key], laravel_code)
            except UnicodeError as e:
                print(e)

        try:
            file = open(filename, 'w+')
            file.write(file_content)
            file.close()
        except UnicodeError as e:
            print(e)

    print('File ' + filename + ' - Matches ' + str(matches_count))

to_file = open(args.destiny + '.map', 'w+')
to_file.write(json.dumps(mapper))
# o_file.write(json.dumps(mapper, sort_keys=True, indent=4, separators=(',', ': '))) # beauty
to_file.close()

print()
print(str(file_count) + " files")

php_array = php.serialize(mapper)
php_array.to_file(args.destiny)
