# Install pyenv prerequisites

echo "127.0.0.1 `hostname`" | sudo tee -a /etc/hosts
sudo apt update
sudo apt upgrade -y
sudo apt install -y unzip build-essential git libreadline-dev zlib1g-dev libssl-dev libbz2-dev libsqlite3-dev

# Installing pyenv is rather straight forward, one simply has to run the command below

curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | sudo -E bash

# Initialise pyenv and add to path
sudo chown ubuntu:ubuntu ~/.pyenv

echo "export PATH=\"/home/ubuntu/.pyenv/bin:$PATH\"" >> ~/.bashrc
echo "eval \"\$(pyenv init -)\"" >> ~/.bashrc
echo "eval \"\$(pyenv virtualenv-init -)\"" >> ~/.bashrc
source ~/.bashrc

# Install python 3.6.5

pyenv install -s 3.6.5
pyenv global 3.6.5

python --version
pip --version

# Create virtual environment

mkdir ~/.virtualenvs
pip install virtualenv
virtualenv -p /home/ubuntu/.pyenv/versions/3.6.5/bin/python ~/.virtualenvs/csw
source ~/.virtualenvs/csw
echo "cd /gds/csw-backend/build" >> ~/.bashrc
echo "source ~/.virtualenvs/csw/bin/activate" >> ~/.bashrc

# Install terraform to enable terraform output

wget https://releases.hashicorp.com/terraform/0.11.10/terraform_0.11.10_linux_amd64.zip
unzip terraform_0.11.10_linux_amd64.zip
./terraform --version
sudo mv terraform /usr/local/bin

# Install aws cli

pip install awscli

mkdir ~/.aws
echo "[default]\nregion = eu-west-1" > ~/.aws/config

# Install the csw-backend codebase
sudo mkdir /gds
sudo chown ubuntu:ubuntu /gds
cd /gds
git clone https://github.com/alphagov/csw-backend.git
