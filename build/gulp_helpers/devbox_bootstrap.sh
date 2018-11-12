#! /bin/bash

current_hostname = `hostname`

if [[ -n $1 && $1 != $current_hostname ]]; then

    sudo hostname $1
    echo $1 | sudo tee /etc/hostname
    # Add hostname alias to /etc/hosts
    echo "127.0.0.1 $1" | sudo tee -a /etc/hosts

fi


# Patch server - do this every time

sudo apt update
sudo apt upgrade -y


# Install pyenv

pyenv_installed = `pyenv --version | grep "pyenv\s+\d+\.\d+\.\d+" | wc -l`

if [ $penv_installed = 0 ]; then

    # Install pyenv prerequisites
    sudo apt install -y unzip build-essential git libreadline-dev zlib1g-dev libssl-dev libbz2-dev libsqlite3-dev

    # Install pyenv
    curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | sudo -E bash -
fi


# Initialise pyenv and add to path

pyenv_config = `cat /home/ubuntu/.bashrc | grep "pyenv" | wc -l`

if [ $pyenv_config = 0 ]; then

    echo "export PATH=\"/home/ubuntu/.pyenv/bin:$PATH\"" >> /home/ubuntu/.bashrc
    echo "eval \"\$(pyenv init -)\"" >> /home/ubuntu/.bashrc
    echo "eval \"\$(pyenv virtualenv-init -)\"" >> /home/ubuntu/.bashrc

    sudo chown -R ubuntu:ubuntu /home/ubuntu/.pyenv

    source /home/ubuntu/.bashrc

fi


# Install python 3.6.5

python_correct_version = `python --version | grep 3.6.5 | wc -l`

if [ $python_correct_version = 0 ]; then

    pyenv install -s 3.6.5
    pyenv global 3.6.5

fi

# Create a 3.6.5 virtual environment

if [ ! -e "/home/ubuntu/.virtualenvs/csw" ]; then
    mkdir -p /home/ubuntu/.virtualenvs
    pip install virtualenv
    virtualenv -p /home/ubuntu/.pyenv/versions/3.6.5/bin/python /home/ubuntu/.virtualenvs/csw

    source /home/ubuntu/.virtualenvs/csw/bin/activate
fi


# Setup default directory and run venv on login

venv_config = `cat /home/ubuntu/.bashrc | grep csw/bin/activate | wc -l`

if [ $venv_config = 0 ]; then
    echo "cd /gds/csw-backend/build" >> /home/ubuntu/.bashrc
    echo "source ~/.virtualenvs/csw/bin/activate" >> /home/ubuntu/.bashrc
fi


# Install terraform to enable terraform output

if [ ! -e "/usr/local/bin/terraform" ]; then
    wget https://releases.hashicorp.com/terraform/0.11.10/terraform_0.11.10_linux_amd64.zip
    unzip terraform_0.11.10_linux_amd64.zip
    ./terraform --version
    sudo mv terraform /usr/local/bin
fi


# Install AWS cli

awscli_installed = `aws --version | grep "aws-cli\s+\d+.\d+.\d+" | wc -l`

if [ $awscli_installed = 0 ]; then
    pip install awscli
fi


npm_installed = `npm --version | grep "\d+.\d+.\d+" | wc -l`

if [ $npm_installed = 0 ]; then

    sudo apt install -y npm

    sudo ln -s /usr/bin/nodejs /usr/bin/node
fi

gulpcli_installed = `gulp --version | grep "CLI version \d+.\d+.\d+" | wc -l`

if [ $gulpcli_installed = 0 ]; then

    sudo npm install -g gulp-cli
fi

# Set AWS defaults

if [ ! -e "/home/ubuntu/.aws/config" ]; then
    mkdir -p /home/ubuntu/.aws
    echo "[default]\nregion = eu-west-1" > /home/ubuntu/.aws/config
fi


# Install the csw-backend codebase

if [ ! -e "/gds/csw-backend" ]; then
    sudo mkdir -p /gds
    sudo chown ubuntu:ubuntu /gds
    cd /gds
    git clone https://github.com/alphagov/csw-backend.git
fi
