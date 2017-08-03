#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# === This file is part of Calamares - <http://github.com/calamares> ===
#
#   Copyright 2014, Pier Luigi Fiorini <pierluigi.fiorini@gmail.com> [packages]
#   Copyright 2016, Mike Krüger <mikekrueger81@gmail.com> [mrpacman]
#
#   Calamares is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Calamares is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Calamares. If not, see <http://www.gnu.org/licenses/>.

import libcalamares
import urllib.request
import subprocess
from libcalamares.utils import check_target_env_call, target_env_call


class PackageManager:

    """ Package manager class.

    :param backend:
    """

    def __init__(self, backend):
        self.backend = backend

    def install(self, pkgs, from_local=False):
        """ Installs packages.

        :param pkgs:
        :param from_local:
        """

        if self.backend == "pacman":
            if from_local:
                pacman_flags = "-U"
            else:
                pacman_flags = "-Sy"

            check_target_env_call(["pacman", pacman_flags, "--noconfirm"
                                  ] + pkgs)

    def remove(self, pkgs):
        """ Removes packages.

        :param pkgs:
        """

        if self.backend == "pacman":
            check_target_env_call(["pacman", "-Rs", "--noconfirm"]
                                  + pkgs)

    def upgrade(self):
        """ upgrades all packages.

        """

        if self.backend == "pacman":
            try:
                check_target_env_call(["pacman", "-Syyu", "--noconfirm"])
            except:
                print("unresolvable package conflicts detected")


def get_language():
    output = libcalamares.globalstorage.value("localeConf")
    lang = output["LANG"]

    parts = lang.split(".")
    if len(parts) < 1:
        return ""

    lang = parts[0].lower()
    lang = lang.replace("_", "-")
    return lang


def install_firefox_language_package():
    lang = get_language()
    command = "pacman -Ss"
    pkgname = "firefox-i18n-"
    encoding = "utf-8"
    update = True
    output = subprocess.check_output(['sh','-c', command, pkgname + lang, "-q"]).decode(encoding)
    if pkgname + lang not in output:
        parts = lang.split("-")
        output = subprocess.check_output(['sh','-c', command, pkgname + parts[0], "-q"]).decode(encoding)
        if pkgname + parts[0] in output:
            pkgname = pkgname + parts[0]
        else:
            update = False
    else:
        pkgname = pkgname + lang

    if update:
        print('[mrpacman] -> Install firefox language package :' + pkgname)
        libcalamares.utils.target_env_call(['pacman', '-Sy', '--noconfirm', 'firefox']) #updating firefox first!
        libcalamares.utils.target_env_call(['pacman', '-S', '--noconfirm', pkgname])


virtualbox = False #global var for virtualbox_check

def virtualbox_check():
    command = "dmidecode -s system-product-name"
    output = subprocess.check_output(['sh','-c', command]).decode('ascii')
    substring = output[0:10].lower()

    global virtualbox
    if substring == "virtualbox":
        virtualbox = True
    else:
        virtualbox = False

    return virtualbox

def packagelist_filter(pkgs, pkg_remove_filter, first_index, last_index):
    new_package_list = []
    for pkg in pkgs:
        part = pkg[first_index:last_index].lower()
        if part != pkg_remove_filter:
            new_package_list.append(pkg)

    return new_package_list


def connected(reference):
    try:
        urllib.request.urlopen(reference, timeout=1)
        return True
    except urllib.request.URLError:
        return False


def run_operations(pkgman, entry):
    """ Call package manager with given parameters.

    :param pkgman:
    :param entry:
    """

    for key in entry.keys():
        if key == "install":
            pkgman.install(entry[key])
        elif key == "remove":
            if virtualbox:
                pkgman.remove(packagelist_filter(entry[key], "virtualbox", 0, 10))
            else:
                pkgman.remove(entry[key])
        elif key == "localInstall":
            pkgman.install(entry[key], from_local=True)


def run():
    """ Calls routine with detected package manager to install locale packages
    or remove drivers not needed on the installed system.

    :return:
    """

    virtualbox_check()

    backend = libcalamares.job.configuration.get("backend")

    if backend not in ("pacman"):
        return "Bad backend", "backend=\"{}\"".format(backend)

    pkgman = PackageManager(backend)
    operations = libcalamares.job.configuration.get("operations", [])

    for entry in operations:
        run_operations(pkgman, entry)

    if connected("http://github.com"):
        #print('[mrpacman] -> updating packages..(this may take several minutes)')
        #pkgman.upgrade()
        install_firefox_language_package()
    else:
        print('[mrpacman] -> updating packages skipped (no internet connection found!)')

    if libcalamares.globalstorage.contains("packageOperations"):
        run_operations(pkgman,
                       libcalamares.globalstorage.value("packageOperations"
                       ))

    return None
