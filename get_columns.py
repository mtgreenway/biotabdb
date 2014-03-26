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

file_types = {}
general_columns = collections.defaultdict(set)
disease_specific = collections.defaultdict(dict)

ignore = ['MANIFEST.txt', 'CHANGES_DCC.txt', 'README_DCC.txt']

for dirent in os.walk('.'):
    if (not dirent[1]) and dirent[2]:

        disease = dirent[0][2:]

        for f_type in [d for d in dirent[2] if d not in ignore]:
            file_format = f_type[len("nationwidechildrens.org_"):-(
                len(disease) + len('.txt'))]

            with open(os.path.join(dirent[0], f_type), 'rb') as f:
                reader = csv.reader(f, delimiter='\t')
                print reader.fieldnames
                header = reader.next()
                print reader.next()
                print reader.next()
                import sys
                sys.exit()
                #print " file ", file_format, disease, " is ", len(header), " columns"
                if file_format not in file_types:
                    file_types[file_format] = collections.defaultdict(int)
                for col in header:
                    file_types[file_format][col] += 1

                disease_specific[disease][file_format] = set(header)


for file_format, header in file_types.items():

    if len(set(header.values())) == 1:
        general_columns[file_format] = set(header.keys())
    else:
        for k, v in header.items():
            if v > 1:
                general_columns[file_format].add(k)

    #print file_format, " general columns ", general_columns[file_format]
    create = "CREATE TABLE %s ( disease varchar, %s );" % (
            file_format.strip("_"), ",".join(
                ["%s text" % c for c in general_columns[file_format]]))
    print create.replace(".", "_")

    for disease in disease_specific:
        if file_format in disease_specific[disease]:
            diff = disease_specific[disease][file_format].difference(
                general_columns[file_format])
            if diff:
                create = "CREATE TABLE %s ( %s );" % ("%s%s" % (
                        file_format, disease), ",".join(
                        ["%s text" % c for c in diff]))
                print create.replace(".", "_")

