#!/bin/bash
DISEASE=$1

base=https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/${DISEASE}/bcr/biotab/clin/
IFS=$'\n'

status=$(curl -s -I ${base}MANIFEST.txt | head -n 1)
if [[ "$status" != *HTTP/1.*\ 200* ]]
then
    echo $status
    echo "$DISEASE has no manifest"
    exit 1
fi

mkdir -p $DISEASE

cd $DISEASE
for line in $(curl -s ${base}MANIFEST.txt)
do
    filename=$(echo $line| python -c "import fileinput
print fileinput.input()[0].split()[1],")
    #if [[ $filename == 'CHANGES_DCC.txt' || $filename == 'README_DCC.txt' || $filename == 'MANIFEST.txt' ]]
    if [[ $filename == 'MANIFEST.txt' ]]
    then
        wget --quiet -O $filename ${base}${filename} &
        continue
    fi

    md5sum -c <(echo $line)
    test=$?
    if [ $test == 0 ]
    then
        :
        #echo "$filename is good"
    else
        wget --quiet -O $filename ${base}${filename} &
    fi
done
