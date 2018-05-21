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
api_old_packets_ct79400="1G5h-OH_x9tSp932snjrhMWRT9b87DqN1"
isolation_forest_countbased_trainct80k="1LbJv9CxcYTMQOKoSpXre8xm9GP-IdHlI"

to_download=(api_old_packets_ct79400 isolation_forest_countbased_trainct80k)

# TODO: make this logic nicer.
for i in {0..1}
do
  echo "Downloading ${to_download[$i]}.pkl"
  python gdrive.py ${!to_download[$i]} ${to_download[$i]}.pkl
done

exit 0
