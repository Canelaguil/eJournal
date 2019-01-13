#!/bin/bash

echo ${1}
if [[ -z ${1} ]]; then
    totest=
else
    totest="-k ${1}"
fi
sha=0
previous_sha=0
source ./venv/bin/activate


test () {
    clear
    pytest src/django/test $totest
    previous_sha=`ls -lR src | sha1sum`
}

while true; do
    sha=`ls -lR src | sha1sum`
    if [[ $sha != $previous_sha ]] ; then
        test
    fi
    read -s -t 1 && test
done
