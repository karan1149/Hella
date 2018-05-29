#!/bin/sh

#
# Fetches some canonical models and datasets for use with the
# model zoo.
#
# NOTE: all data loaded is assumed to have been pickled
#       using Python 3.
#


# Ensure that we are running with python3
version="$(python --version)"
version=($version)
if  [[ ${version[1]} != 3* ]];
then
    echo "You should be running with Python 3."
    exit
fi

# Variable names mapping the name of the file to be downloaded
# with their unique Google Drive ID.

# Data
assets="1ph8A_LM6dFV0GKl3OF0dDcIT3fnGnAly"

to_download_assets=(assets)

# TODO: make this logic nicer.
for i in {0..0}
do
  echo "Downloading ${to_download_assets[$i]}.zip for training"
  python ../zoo/gdrive.py ${!to_download_assets[$i]} assets.zip
  mkdir assets
  unzip assets.zip -d assets/
done

exit 0
