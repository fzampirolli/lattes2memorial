#!/bin/bash
#sudo apt update && sudo apt -y upgrade

#source lattesEnv/bin/activate

folder=$1   #${PWD##*/}          # to assign to a variable
folder=${folder:-/}        # to correct for the case where PWD=/

cd tmp

echo $folder
#chmod 777 -R $folder

cd $folder

../../lattesEnv/bin/python lattes2memorial.py

cd ../

zip -r ${folder}_lattes.zip $folder

echo "compactado "$folder"_lattes.zip"
rm -rf $folder

cd ../

#deactivate
