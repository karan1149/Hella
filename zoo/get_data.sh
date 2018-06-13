#!/bin/sh

#
# Fetches some canonical models and datasets for use with the
# model zoo.
#
# NOTE: all data loaded is assumed to have been pickled
#       using Python 3.
#


# Ensure that we are running with python2
ispy2=`python -c 'import sys; print sys.version_info > (2, 7) and sys.version_info < (3, 0)'`
if [ $ispy2 != "True" ];
then
    echo $ispy2
    echo "You should be running with Python 2."
    exit
fi

# Variable names mapping the name of the file to be downloaded
# with their unique Google Drive ID.

# Data
data="https://drive.google.com/open?id=17AdX_puvVC3c7JqW6iHB7Ys38IOtqFdR"

to_download_data=(data)

for i in {0..0}
do
  echo "Downloading ${to_download_data[$i]}.zip for training"
  python gdrive.py ${!to_download_assets[$i]} assets.zip
  unzip zoo_models_datasets_final.zip
done

exit 0

