# This calls https://github.com/pyenv/pyenv-installer and runs the commands that have to be run afterwards, and THEN it installs python 3.7


########################################
# Step 1: pyenv-installer

# Install prerequirements
# Currently accounted for: Debian/Ubuntu & Alpine
# Thanks to https://stackoverflow.com/a/677212 for teaching me how to check for commands
if command -v apt-get &> /dev/null
then
    sudo apt-get update
    sudo apt-get upgrade
    echo "Detected debian-like, installing dependancies accordingly"
    sudo apt-get update; sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
        libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
elif command -v apk &> /dev/null
then
    apk update
    echo "Detected alpine-like, installing dependancies accordingly"
    apk add --no-cache git bash build-base libffi-dev openssl-dev bzip2-dev zlib-dev readline-dev sqlite-dev 
    echo "Also, add bash. Alpine doesn't have it pre-installed, but pyenv needs a stronger shell than sh/Bourne"
    apk add bash
fi

# Install pyenv through the installer
curl https://pyenv.run | bash

########################################
# Step 2: 

# From the env installer:
# (The below instructions are intended for common
# shell setups. See the README for more guidance
# if they don't apply and/or don't work for you.)

# Add pyenv executable to PATH and
# enable shims by adding the following
# to ~/.profile:

#export PYENV_ROOT="$HOME/.pyenv"
#export PATH="$PYENV_ROOT/bin:$PATH"
#eval "$(pyenv init --path)"
printf '%s\n' 'export PYENV_ROOT="$HOME/.pyenv"' 'export PATH="$PYENV_ROOT/bin:$PATH"' 'eval "$(pyenv init --path)"' >>  ~/.profile

# NOTE: there was some .bashrc stuff but it didn't work and I can't replicate the warning that told me to change it
# Keep an eye out for issues in terms of this

# Make sure to restart your entire logon session
# for changes to profile files to take effect.

# Restart your shell so the path changes take effect:
exec $SHELL

########################################

# Step 3: install py 3.7.11, set it as default for the current directory

pyenv install 3.7.11
pyenv local 3.7.11
python -m pip install git+git://github.com/wellcometrust/deep_reference_parser.git#egg=deep_reference_parser

