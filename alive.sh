#/bin/bash

while true
do
sleep 2
if [ $(ps aux|grep run.py|grep -v grep|grep $1|wc -l) -ne "1" ];then
echo "Iniciando..."
/usr/local/bin/python2.7 /home/zap/run.py $1
fi
done
