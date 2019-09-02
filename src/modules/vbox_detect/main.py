#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import libcalamares
import subprocess
from libcalamares.utils import check_target_env_call, target_env_call
from libcalamares.utils import *
import os


def run():
    """ Calls routine to detect Virtualbox.

    :return:
    """
    root_mount_point = libcalamares.globalstorage.value("rootMountPoint")
    try:
     os.system("lspci >vbox.txt")
    except:
     pass

    if not 'VirtualBox' in open('vbox.txt').read():
     try:
      subprocess.check_call(["pacman", "-Rns", "virtualbox-guest-utils", "virtualbox-guest-dkms", "--noconfirm", "--root", root_mount_point])
     except:
      pass

    return None
