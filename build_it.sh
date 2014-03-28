#!/bin/bash

#rm */*.fix

#for i in $(cat cancers);do ./getfiles.sh $i;done

rec_fix () {
    sed "$(perl -ne "print \$1 if /line (\d*)/" < $2)d" $1 > $1.fix
    $postgres $database -c "copy $table FROM '$1.fix'" > /dev/null 2>$2.fix
    if [ $? == 0 ]
    then
        rm $2.fix
    else
        cat $2.fix
        rec_fix $1.fix $2.fix
    fi
}

base_dir="/home/ubuntu/tcga/"
postgres="sudo -iu postgres /usr/local/pgsql/bin/psql"
database="tcga"
rundir=.run

mkdir -p $rundir

$postgres -c "drop database $database"
$postgres -c "create database $database"

echo "creating tables ..."

python get_columns.py --separate | $postgres $database > /dev/null

echo "filling tables ..."

for file_format in $(python get_columns.py --list_tables)
do
    disease=$(echo $file_format| python -c "import fileinput
print fileinput.input()[0].split('_')[-1],")
    table=$(echo $file_format| python -c "import fileinput
print fileinput.input()[0].replace('.','_'),")

    (
        filename=nationwidechildrens.org_$file_format.txt
        tsvfile=${base_dir}$disease/$filename

        $postgres $database -c "copy $table FROM '$tsvfile'" > /dev/null 2>$rundir/$filename
        if [ $? == 0 ]
        then
            rm $rundir/$filename
        else
            rec_fix $tsvfile $rundir/$filename
        fi
    ) &
done

cat $rundir/* > .errors

rm -rf $rundir
