#!/bin/bash

#rm */*.fix

for i in $(cat cancers);do ./getfiles.sh $i;done

rec_fix () {
    local tsv_file_name=$1
    local error_file_name=$2
    local table_name=$3

    echo "TSV FILE NAME "$tsv_file_name
    echo "ERROR FILE NAME "$error_file_name

    sed "$(perl -ne "print \$1 if /line (\d*)/" < $error_file_name)d" $tsv_file_name > $tsv_file_name.fix
    $postgres $database -c "copy $table_name FROM '$tsv_file_name.fix'" > /dev/null 2>$error_file_name.fix
    if [ $? == 0 ]
    then
        rm $error_file_name.fix
        rm $tsv_file_name.fix
    else
        cat $error_file_name.fix
        rec_fix $tsv_file_name.fix $error_file_name.fix $table_name
        rm $tsv_file_name.fix
    fi
}

base_dir="$(pwd)/"
postgres="sudo -iu postgres psql"
database="tcga"
rundir=.run

set -e

mkdir -p $rundir

$postgres -c "CREATE USER $db_user password '$db_password';"
$postgres -c "drop database $database"
$postgres -c "create database $database"

echo "creating tables ..."

python get_columns.py --separate | $postgres $database > /dev/null

echo "filling tables ..."

set +e

for file_format in $(python get_columns.py --list_tables)
do
    disease=$(echo $file_format| python -c "import fileinput
print fileinput.input()[0].split('_')[-1],")
    table=$(echo $file_format| python -c "import fileinput
print fileinput.input()[0].replace('.','_'),")

    (
        filename=nationwidechildrens.org_$file_format.txt
        tsvfile=${base_dir}$disease/$filename

        $postgres -c "GRANT ALL ON $table TO $db_user;"
        $postgres $database -c "copy $table FROM '$tsvfile'" > /dev/null 2>$rundir/$filename
        if [ $? == 0 ]
        then
            rm $rundir/$filename
        else
            rec_fix $tsvfile $rundir/$filename $table
        fi
    )
done

cat $rundir/* > .errors
rm -rf $rundir
