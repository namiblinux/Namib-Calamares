#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import libcalamares
import subprocess
from libcalamares.utils import check_target_env_call, target_env_call
from libcalamares.utils import *
import os


def run():
    """ Calls routine to create kernel initramfs image.

    :return:
    """
    root_mount_point = libcalamares.globalstorage.value("rootMountPoint")
    try:
     subprocess.check_call(["cp", "/run/archiso/bootmnt/arch/boot/x86_64/vmlinuz", root_mount_point + "/boot/vmlinuz-linux"])
    except:
     pass # doing nothing on exception

    return None
