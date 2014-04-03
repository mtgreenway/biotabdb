#  Copyright 2013 Open Cloud Consortium
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import os
import csv
import collections
import argparse


def list_tables():
    disease_specific = collections.defaultdict(dict)
    ignore = ['MANIFEST.txt', 'CHANGES_DCC.txt', 'README_DCC.txt', 'BCRBiotabREADME.html']
    file_types = {}
    for dirent in os.walk('.'):
        if dirent[0].startswith("./."):
            continue
        if (not dirent[1]) and dirent[2]:

            disease = dirent[0][2:]

            for f_type in [d for d in dirent[2] if d not in ignore]:
                file_format = f_type[len("nationwidechildrens.org_"):-len('.txt')]
                print file_format


def small_bad_tables():
    disease_specific = collections.defaultdict(dict)
    ignore = ['MANIFEST.txt', 'CHANGES_DCC.txt', 'README_DCC.txt', 'BCRBiotabREADME.html']
    file_types = {}
    for dirent in os.walk('.'):
        if dirent[0].startswith("./."):
            continue
        if (not dirent[1]) and dirent[2]:

            disease = dirent[0][2:]

            for f_type in [d for d in dirent[2] if d not in ignore]:
                file_format = f_type[len("nationwidechildrens.org_"):-len('.txt')]
                with open(os.path.join(dirent[0], f_type), 'rb') as f:
                    reader = csv.reader(f, delimiter='\t')
                    header = reader.next()
                    if len(header) != len(set(header)):
                        header = ["%s%s" % (v, i) if v in header[i+1:] else v
                            for i, v in enumerate(header)]


                    create = "CREATE TABLE %s ( %s );" % ("%s" % file_format
                            , ",".join(
                            ["%s text" % c for c in header]))
                    print create.replace(".", "_")


def file_type_info():
    disease_specific = collections.defaultdict(dict)
    ignore = ['MANIFEST.txt', 'CHANGES_DCC.txt', 'README_DCC.txt', 'BCRBiotabREADME.html']
    file_types = {}
    for dirent in os.walk('.'):
        if dirent[0].startswith("./."):
            continue
        if (not dirent[1]) and dirent[2]:

            disease = dirent[0][2:]

            for f_type in [d for d in dirent[2] if d not in ignore]:
                file_format = f_type[len("nationwidechildrens.org_"):-(
                    len(disease) + len('.txt'))]
                print file_format

                with open(os.path.join(dirent[0], f_type), 'rb') as f:
                    reader = csv.reader(f, delimiter='\t')
                    header = reader.next()
                    if file_format not in file_types:
                        file_types[file_format] = collections.defaultdict(int)
                    for col in header:
                        file_types[file_format][col] += 1

                    disease_specific[disease][file_format] = set(header)
    return file_types, disease_specific

def get_general_columns(file_types):
    general_columns = collections.defaultdict(set)
    for file_format, header in file_types.items():

        if len(set(header.values())) == 1:
            general_columns[file_format] = set(header.keys())
        else:
            for k, v in header.items():
                if v > 1:
                    general_columns[file_format].add(k)

    return general_columns


def general_column_creates(file_types, general_columns):
    for file_format, header in file_types.items():
        create = "CREATE TABLE %s ( disease varchar, %s );" % (
                file_format.strip("_"), ",".join(
                    ["%s text" % c for c in general_columns[file_format]]))
        yield create.replace(".", "_")


def specific_column_creates(file_types, general_columns, disease_specific):
    for file_format, header in file_types.items():

        for disease in disease_specific:
            if file_format in disease_specific[disease]:
                diff = disease_specific[disease][file_format].difference(
                    general_columns[file_format])
                if diff:
                    create = "CREATE TABLE %s ( %s );" % ("%s%s" % (
                            file_format, disease), ",".join(
                            ["%s text" % c for c in diff]))
                    yield create.replace(".", "_")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--separate", action="store_true")
    parser.add_argument("--list_tables", action="store_true")
    args = parser.parse_args()
    if args.separate:
        small_bad_tables()
    elif args.list_tables:
        list_tables()

#    file_types, disease_specific = file_type_info()
#    general_columns = get_general_columns(file_types)
#    for i in general_column_creates(file_types, general_columns):
#        print i

if __name__ == "__main__":
    main()
