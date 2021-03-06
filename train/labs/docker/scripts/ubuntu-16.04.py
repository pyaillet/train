#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


import requests


# helper functions
def check_url(path, version):
    """Check for valid URL"""
    print 'Checking URL: https://{0}/docker-{1}'.format(path, version)
    return 'https://{0}/docker-{1}'.format(path, version)


def get_txt(path, version):
    """Custom Docker install text"""
    txt = 'curl -sSL https://get.docker.com/ | sh\n'.format(path) + \
          'mv /usr/bin/docker /usr/bin/docker.org\n' + \
          'wget https://{0}/docker-{1} -O /usr/bin/docker\n'.format(path, version) + \
          'chmod +x /usr/bin/docker\n'
    return txt


def get_custom(prompt):
    """Prompt for custom Docker version"""

    version = raw_input(prompt)
    if 'rc' in version:
        path = 'test.docker.com/builds/Linux/x86_64'
    elif 'dev' in version:
        path = 'master.dockerproject.org/linux/amd64'
    else:
        path = 'get.docker.com/builds/Linux/x86_64'

    r = requests.head(check_url(path, version))
    if r.status_code != 200:
        print 'Unable to locate specified version.'
        txt = get_custom('\nEnter a different version: ')
    else:
        txt = get_txt(path, version)

    return txt


# prompts
os.system('clear')
docker = raw_input("""
Which version of Docker do you want to install?

  - latest (default)
  - cs
  - rc
  - experimental (nightly)
  - master (github master branch)
  - custom

Enter version (Press enter for default): """)

# example urls
#https://get.docker.com/builds/Linux/x86_64/docker-latest
#https://test.docker.com/builds/Linux/x86_64/docker-1.6.0-rc6
#https://master.dockerproject.com/linux/amd64/docker-1.5.0-dev

docker = docker.lower()
if docker == '' or docker =='latest':
    txt = 'curl -sSL https://get.docker.com/ | sh'
elif docker == 'cs':
    txt = "curl -s 'https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | apt-key add --import\n" + \
          'echo "deb https://packages.docker.com/1.13/apt/repo ubuntu-xenial main" | tee /etc/apt/sources.list.d/docker.list\n' + \
          'apt-get update && apt-get install -y docker-engine\n'

elif docker == 'rc':
    txt = 'curl -faSL https://test.docker.com/ | sh'
elif docker == 'experimental':
    txt = 'curl -fsSL https://experimental.docker.com/ | sh'
elif docker == 'master':
    r = requests.get('https://master.dockerproject.org/version')
    txt = get_txt('master.dockerproject.org/linux/amd64', r.text)
elif docker == 'custom':
    txt = get_custom('Enter version: ')
else:
    print "ERROR: Not a valid option."
    sys.exit()


# instance configs
PRIMARY_OS = 'Ubuntu-16.04'
PRIMARY = '''#!/bin/sh

FQDN="{{fqdn}}"

export DEBIAN_FRONTEND=noninteractive

# locale
locale-gen en_US.UTF-8

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

# updates
apt-get update && apt-get install -y \
    apt-transport-https \
    git \
    jq \
    linux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    tree

# docker
{0}

systemctl start docker
sleep 15

usermod -aG docker ubuntu

# compose
curl -L https://github.com/docker/compose/releases/download/1.11.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

{{dinfo}}
reboot
'''.format(txt)

# Script to use if launching from a custom lab AMI image
AMIBUILD = '''#!/bin/sh
#
FQDN="{{fqdn}}"

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

{{dinfo}}
reboot
'''.format()


def pre_process():
    """Executed before launching instances in AWS"""
    pass

def post_process():
    """Executed after launching instances in AWS"""
    pass
