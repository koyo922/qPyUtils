#!/usr/bin/env bash

set -e
#set -xv
#PS4='$LINENO: '

# Usage:
#
# git clone ...
# cd ...
# bash ./src/main/scripts/bootstrap_dev.sh

PY_VERSIONS=("2.7.14" "3.6.5")
VENV_PREFIX=qpyutil

#-------------------- config
if command -v proxychains4 > /dev/null ; then
    PROXY=proxychains4
else
    PROXY=
fi

if ! grep pyenv ~/.bash_profile > /dev/null ; then
    cat >> ~/.bash_profile <<-'EOF'
	export PATH="~/.pyenv/bin:$PATH"
	eval "$(pyenv init -)"
	eval "$(pyenv virtualenv-init -)"
	export PYENV_VIRTUALENV_DISABLE_PROMPT=1
EOF
fi

if [ ! -f ~/.pip/pip.conf ]; then
    mkdir -p ~/.pip
    cat >> ~/.pip/pip.conf <<-'EOF'
	[global]
	trusted-host = mirrors.aliyun.com
	index-url = http://mirrors.aliyun.com/pypi/simple
EOF
fi

#-------------------- ensure pyenv
if ! command -v pyenv > /dev/null ; then
    $PROXY curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
fi
source ~/.bash_profile

#-------------------- virtualenv pybuilder
for PYVER in ${PY_VERSIONS[@]}; do
    if ! pyenv versions | grep ${PYVER} > /dev/null ; then
        $PROXY wget https://www.python.org/ftp/python/${PYVER}/Python-${PYVER}.tar.xz -P ~/.pyenv/cache/
        pyenv install --skip-existing --verbose ${PYVER}
    fi

    VENV_NAME=${VENV_PREFIX}-${PYVER}
    if ! pyenv virtualenvs | grep ${VENV_NAME} > /dev/null ; then
        pyenv virtualenv ${PYVER} ${VENV_NAME}
        pyenv activate ${VENV_NAME}
        pip install -r requirements-dev.txt

        echo "******************** preparing dev environment in python-${PYVER}"
        pyb install_dependencies -v
    fi
done

echo "---------- done configuring development environment"
echo -e "we are in:\n $(pyenv versions)\n"
echo "to switch: just type 'pyenv activate <venv_name>'"
