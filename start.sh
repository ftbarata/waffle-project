#!/bin/bash

if [ ! -z "$1" ];then
	if [ -s "$1" ];then
		i=$(basename $1)
		echo "INICIADO ROBO DA CONFIGURACAO: $i ."
		screen -d -m -S "$i" ~/alive.sh $1
		echo -ne "\n"
		echo "lista de robos ativos:"
		screen -list
		echo -ne "\n"
		echo "Execute screen -r <identificador> para conectar na sessao desejada."
	else
		echo "Arquivo $1 nao encontrado ou vazio."
	fi
else
echo "Arquivo de configuracao do robo nao informado."
fi

