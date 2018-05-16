#!/bin/bash

# install Homebrew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# install scapy dependencies using Homebrew
brew install --with-python libdnet
brew install https://raw.githubusercontent.com/secdev/scapy/master/.travis/pylibpcap.rb
sudo brew install --with-python libdnet
sudo brew install https://raw.githubusercontent.com/secdev/scapy/master/.travis/pylibpcap.rb
