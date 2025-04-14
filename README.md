Tested the code with python 3.13 and expected to work for any python version > 3.7

Install python3 with version >= 3.7, with pip and virtual env
Create a virtual environment and install requirements by running:

pip3 install -r requirements.txt

The driver program is in main.py which needs to be executed with a run-time parameter
in the below manner:

python3 src/main.py -a <YOUR_WALLET_ADDRESS>

Here, you may pass the desired wallet address, and the output shall be downloaded in
the folder data/output/ relative to this repository.

API_TOKEN is public and hard-coded at the moment, can be externalised using ENV variables
in an actual production deployment