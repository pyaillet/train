#!/usr/bin/env python

import sys
from distutils.util import strtobool

def yn_prompt(query):
    """Generic Y/N Prompt"""

    sys.stdout.write('%s [y/n]: ' % query)
    val = raw_input()
    try:
        ret = strtobool(val)
    except ValueError:
        sys.stdout.write('Please answer with a y/n\n')
        return yn_prompt(query)
    return ret


# prompts
ubuntu_pass = raw_input("Enter password for 'ubuntu' user (letters and digits only): ")
install = yn_prompt("\nInstall UCP using 'non-interactive' mode on the controller instance?")

if install:
    txt = 'docker run --rm --name ucp -v /var/run/docker.sock:/var/run/docker.sock docker/ucp install --host-address $(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)'
else:
    txt = 'docker run --name ucp --rm -v /var/run/docker.sock:/var/run/docker.sock docker/ucp images'


# scripts
PRIMARY_OS = 'Ubuntu-16.04'
CONTROLLER = '''#!/bin/sh

FQDN="{{fqdn}}"

export DEBIAN_FRONTEND=noninteractive

# locale
locale-gen en_US.UTF-8

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

# packages
curl -s 'https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | apt-key add --import
echo "deb https://packages.docker.com/1.13/apt/repo ubuntu-xenial main" | tee /etc/apt/sources.list.d/docker.list
apt-get update && apt-get install -y \
    apt-transport-https \
    docker-engine \
    git \
    htop \
    jq \
    inux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    seccomp \
    strace \
    tree

systemctl start docker
sleep 15

# compose
curl -L https://github.com/docker/compose/releases/download/1.11.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# download/install upc
{0}

# password authentication
echo ubuntu:{1} | chpasswd
sed -i 's|[#]*PasswordAuthentication no|PasswordAuthentication yes|g' /etc/ssh/sshd_config
service ssh restart

usermod -aG docker ubuntu

{{dinfo}}
reboot
'''.format(txt, ubuntu_pass)

NODE = '''#!/bin/sh

FQDN="{{fqdn}}"

export DEBIAN_FRONTEND=noninteractive

# locale
locale-gen en_US.UTF-8

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

# packages
curl -s 'https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e' | apt-key add --import
echo "deb https://packages.docker.com/1.13/apt/repo ubuntu-xenial main" | tee /etc/apt/sources.list.d/docker.list
apt-get update && apt-get install -y \
    apt-transport-https \
    docker-engine \
    git \
    htop \
    jq \
    inux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    seccomp \
    strace \
    tree

systemctl start docker
sleep 15

usermod -aG docker ubuntu

# compose
curl -L https://github.com/docker/compose/releases/download/1.11.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# download ucp images (no install)
docker run --name ucp --rm -v /var/run/docker.sock:/var/run/docker.sock docker/ucp images

# password authentication
echo ubuntu:{0} | chpasswd
sed -i 's|[#]*PasswordAuthentication no|PasswordAuthentication yes|g' /etc/ssh/sshd_config
service ssh restart

{{dinfo}}
reboot
'''.format(ubuntu_pass)

# Script to use if launching from a custom lab AMI image
AMIBUILD = '''#!/bin/sh

FQDN="{{fqdn}}"

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

# password authentication
echo ubuntu:{0} | chpasswd
sed -i 's|[#]*PasswordAuthentication no|PasswordAuthentication yes|g' /etc/ssh/sshd_config
service ssh restart

{{dinfo}}
reboot
'''.format(ubuntu_pass)

def pre_process():
    """Anything added to this function is executed before launching the instances"""
    pass

def post_process():
    """Anything added to this function is executed after launching the instances"""
    pass
