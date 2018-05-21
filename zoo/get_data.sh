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
api_old_packets_500_count="1PHkENtFJFWZ7fwt16VtRDF5tuQqm8Iz9"

# Models
isolation_forest_countbased_trainct80k="1Dqn2VOMC44LB-JsU55qCol3ZokF78COm"

to_download_models=(isolation_forest_countbased_trainct80k)
to_download_data=(api_old_packets_500_count)

# TODO: make this logic nicer.
for i in {0..0}
do
  echo "Downloading model ${to_download_models[$i]}.pkl"
  python gdrive.py ${!to_download_models[$i]} models/${to_download_models[$i]}.pkl

  echo "Downloading data ${to_download_data[$i]}.pkl"
  python gdrive.py ${!to_download_data[$i]} datasets/${to_download_data[$i]}.pkl
done

exit 0
