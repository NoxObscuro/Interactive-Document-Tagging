#!/usr/bin/env bash

CURRENT_DIR=$(pwd)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

echo "# Building 'idt-preprocessing' docker image... This might take several minutes."
cd ${SCRIPT_DIR}/source/preprocessing
sudo docker build -t idt-preprocessing . 

echo
echo "# Building 'idt-app' docker image..."
cd ${SCRIPT_DIR}/source/web-app
sudo docker build -t idt-app .

echo "# Creating database, import and export directory in ${SCRIPT_DIR}/application"
mkdir -p ${SCRIPT_DIR}/application/{database,import,export}


echo 
echo "# Finished setup..."
echo "You can customize the commandline parameters of the docker-compose-preprocessing.yml"
echo "in the application directory to fit your needs. Read the README.md to get an"
echo "overview of the usage."
echo
echo "After customizing the docker-compose-preprocessing.yml run:"
echo "sudo docker compose -f ${SCRIPT_DIR}/application/docker-compose-preprocessing.yml up"
echo "To start the preprocessing."
