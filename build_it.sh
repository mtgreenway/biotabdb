#!/bin/bash

base_dir="/home/ubuntu/tcga/"
postgres="sudo -iu postgres /usr/local/pgsql/bin/psql"
database="tcga"

$postgres -c "drop database $database"
$postgres -c "create database $database"
python get_columns.py --separate | $postgres $database

for file_format in $(python get_columns.py --list_tables)
do
    disease=$(echo $file_format| python -c "import fileinput
print fileinput.input()[0].split('_')[-1],")
    table=$(echo $file_format| python -c "import fileinput
print fileinput.input()[0].replace('.','_'),")

    $postgres $database -c "copy $table FROM '${base_dir}$disease/nationwidechildrens.org_$file_format.txt'"
done

