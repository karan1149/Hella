#!/bin/sh

#
# Fetches some canonical models and datasets for use with the
# model zoo.
#
# NOTE: all data loaded is assumed to have been pickled
#       using Python 2.
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
assets="1ph8A_LM6dFV0GKl3OF0dDcIT3fnGnAly"

to_download_assets=(assets)

for i in {0..0}
do
  echo "Downloading ${to_download_assets[$i]}.zip for training"
  python ../zoo/gdrive.py ${!to_download_assets[$i]} assets.zip
  mkdir assets
  unzip assets.zip -d assets/
done

exit 0
