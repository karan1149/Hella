## Demo Day Simulation

Download data from (here)[https://www.ll.mit.edu/ideval/data/1999/training/week2/index.html] as required (use outside.tcpdump for each day). We use week1_monday.tcpdump, week1_tuesday.tcpdump, week1_wednesday.tcpdump, week1_thursday.tcpdump, week1_friday.tcpdump, and week2_thursday.tcpdump, all put in the /ml/data directory.

To run, navigate to /ml, activate your virtualenv, and run:

```
python ../simulation/simulate.py
```

## Breakathon

Download asset data from (here)[https://drive.google.com/file/d/1vQlPmA8RF3WMP40IANaX7AoAhfktQv4L/view?usp=sharing]. Unzip the file and place its contents (mnultiple files not a singular folder) in ./simulation/assets.

Steps:
1. Create two datasets (train and test) from two separate assets (.csv files) using the create_dataset.py command line interface. Save them as .pkl files.
2. Train a model on the train dataset and save it to ./simulation/models using the simulate.py command line interface. Save it as a .pkl file.
3. Test a model on the test dataset using the simulate.py command line interface.
4. Rinse. Repeat.

To run, navigate to /simulation, activate your virtualenv, and run:

```
sudo python3 ../simulation/simulate.py -h
```

*sudo and python3 are required by scapy