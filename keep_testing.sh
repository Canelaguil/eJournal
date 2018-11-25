
prev=0
while :
do
    while [ `stat -c %Y src/django/test/test_${1}.py` -eq $prev ]
    do
        sleep 1
    done
    prev=`stat -c %Y src/django/test/test_${1}.py`
    clear
    bash -c "source ./venv/bin/activate && pytest src/django/test -k ${1} && deactivate"
done
