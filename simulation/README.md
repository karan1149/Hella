## Packet Simulation and Data Generation

This folder contains scripts that run the SeeR system on three different tasks: training dataset creation, model training, and test dataset creation.

### Train Dataset Creation

To train a dataset, you first need to download lat/long assets, which the dataset creation script uses to generate training data that resembles realistic car network traffic.

To download these assets, run:

```sh get_assets.sh```

This will create an `assets` folder in the current directory containing the required asset files.

To actually create a dataset, use the `dataset.py` script.

```sudo python dataset.py --asset_file assets/asset107.csv --data_file my_output_training_dataset.pkl```

Note that sudo is required for Scapy. The `asset_file` can be any file in the assets directory downloaded by the above script, where smaller asset files will generally produce smaller datasets. The `data_file` is the output `.pkl` file. After the script is complete, the `.pkl` file will contain an array of Scapy packets resembling realistic car network traffic. You can use the `-h` flag with this script at any point to get help.

Note that you may encounter occasional timeouts while this script runs, which should not cause any problems.

### Model Training

Once a training dataset has been created, you can train the model using the `train.py` script.

```sudo python train.py --data_file my_output_training_dataset.pkl --model_file my_output_model.pkl```

The `data_file` is the `.pkl` file containing a training dataset, generated as the output of the previous step. The `model_file` is the filepath for the output model, which should also be a `.pkl` file. You can use the `-h` flag with this script at any point to get help.

### Test Dataset Creation

Once you have a trained model, you can test it using the `test.py` script. You will likely want to [create an additional dataset](https://github.com/cs210/Hella/tree/master/simulation#train-dataset-creation) for testing.

```python test.py -d my_output_pretest_dataset.pkl -m my_output_model.pkl -o my_output_test_dataset.pkl -a fuzz```

The `--out_file` argument saves the test data to a pkl file once the simulation is complete. The `--attack_type` argument specifies which type of attack to inject (to test pure data, omit this argument). Currently `syn-flood`, `fuzz`, and `teardrop` are the supported attack types.

Additionally, the `train_to_test_random.py` script provides a dummy conversion from a training dataset to a test dataset.
