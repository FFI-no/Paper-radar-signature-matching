#!/bin/bash

read -p "This script will use pip to install Python packages. You might want to do this in a suitable virtual environment. Do you want to proceed? (y/n) " yn

case $yn in 
	[yY] ) echo "Proceeding";;
	* ) echo "Exiting";
		    exit;;
esac

mpspdz="$(python -c 'import settings;print(settings.mpspdz_location)')"

cp MPC_Files/classifier_single_db_ors.mpc ${mpspdz}Programs/Source/classifier_single_db_ors.mpc
cp MPC_Files/classifier_double_db_ors.mpc ${mpspdz}Programs/Source/classifier_double_db_ors.mpc
cp MPC_Files/classifier_triple_db_ors.mpc ${mpspdz}Programs/Source/classifier_triple_db_ors.mpc
cp MPC_Files/classifier_quadruple_db_ors.mpc ${mpspdz}Programs/Source/classifier_quadruple_db_ors.mpc

${mpspdz}compile.py -l -F 22 classifier_single_db_ors
${mpspdz}compile.py -l -F 22 classifier_double_db_ors
${mpspdz}compile.py -l -F 22 classifier_triple_db_ors
${mpspdz}compile.py -l -F 22 classifier_quadruple_db_ors

pip install pygame
pip install pandas
pip install numpy
pip install scikit-learn
pip install kneed
pip install seaborn
pip install matplotlib

