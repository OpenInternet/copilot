#!/usr/bin/env bash
#
# This file is part of copilot, a censorship simulating access point.
# Copyright © 2016 seamus tuohy, <code@seamustuohy.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

# Setup

#Bash should terminate in case a command or chain of command finishes with a non-zero exit status.
#Terminate the script in case an uninitialized variable is accessed.
#See: https://github.com/azet/community_bash_style_guide#style-conventions
set -e
set -u

# TODO remove DEBUGGING
#set -x

# Read Only variables

#readonly PROG_DIR=$(readlink -m $(dirname $0))
#readonly readonly PROGNAME=$(basename )
#readonly PROGDIR=$(readlink -m $(dirname ))

# Get the copilot source
# If this is missing then things have REALLY gone wrong.
# And the script will tell you this when it fails
source /etc/opt/copilot


main() {
    check_core
    check_flask
    check_nginx
    check_plugins
    check_supervisor
}

check_core() {
    check_exist "CoPilot repository" "/home/www/copilot" ""
    check_exist "CoPilot global var config" "/etc/opt/copilot" ""
    apt_installed "python-dev"
    apt_installed "curl"
    apt_installed "python-pysqlite2"
    apt_installed "python-pip"
    apt_installed "usbmount"
    apt_installed "build-essential"
    apt_installed "nginx"
    apt_installed "supervisor"
    apt_installed "python-pip"
    apt_installed "avahi-daemon"
    apt_installed "haveged"
    apt_installed "ntp"
    apt_installed "python-dev"
    apt_installed "git"
    pip_installed "Flask-SQLAlchemy"
    pip_installed "flask-wtf"
    pip_installed "flask-bcrypt"
    pip_installed "Flask-Login"
}

check_flask() {
    check_exist "CoPilot instance" "/home/www/copilot/instance" ""
    check_exist "CoPilot Flask runner" "/home/www/copilot/run.py" ""
    check_exist "CoPilot Flask config" "/home/www/copilot/instance/config.py" ""
    check_exist "CoPilot blockpage Flask config" "/home/www/copilot/instance/bp_config.py" ""
    check_string_exist "CSRF key for copilot" "^CSRF_SESSION_KEY\s=\s" "${COPILOT_DIR}/instance/config.py"
    check_string_exist "CSRF key for copilot blockpage" "SECRET_KEY\s=\s" "${COPILOT_DIR}/instance/config.py"
}

check_nginx() {
    check_exist "nginx sites available for copilot" "/etc/nginx/sites-available/copilot" ""
}

check_plugins() {
    check_exist "Copilot plugins repo" "${COPILOT_PLUGINS_DIRECTORY}/plugins" ""
    check_string_not_exist "Supervisor plugin dir" "COPILOT_PLUGINS_DIRECTORY" "/etc/supervisor/conf.d/supervisord.conf"
}

check_supervisor() {
    check_exist "Supervisor config" "/etc/supervisor/conf.d/supervisord.conf" ""
    check_string_not_exist "Supervisor plugin dir" "PLUGIN_DIR_REPLACE_STRING" "/etc/supervisor/conf.d/supervisord.conf"
    check_string_not_exist "Supervisor profile dir" "COPILOT_PROFILE_DIR_REPLACE_STRING" "/etc/supervisor/conf.d/supervisord.conf"
    check_string_not_exist "Supervisor plugin dir" "COPILOT_TEMP_DIR_REPLACE_STRING" "/etc/supervisor/conf.d/supervisord.conf"
    check_string_not_exist "Supervisor plugin dir" "PLUGIN_DIR_REPLACE_STRING" "/etc/supervisor/conf.d/supervisord.conf"
    check_string_not_exist "Supervisor plugin dir" "COPILOT_DEFAULT_DIR_REPLACE_STRING" "/etc/supervisor/conf.d/supervisord.conf"
}

check_string_not_exist() {
    # Check that a regex string does NOT appears in a file
    local info="$1"
    local regex="$2"
    local path="$3"
    if grep -Exq "${regex}" "${path}"
    then
        local ERROR="${info} placeholder string ${regex} should NOT be found in ${path} it should have been replaced by an actual value"
        error_msg "$ERROR"
    else
        good_msg "${info} placeholder string not found."
    fi
}

check_string_exist() {
    # Check that a regex string appears in a file
    local info="$1"
    local regex="$2"
    local path="$3"
    if grep -Exq "${regex}" "${path}"
    then
        good_msg "${info} string found."
    else
        local ERROR="${info} string ${regex} should be found in ${path}"
        error_msg "$ERROR"
    fi
}


check_exist() {
    # Check if a file exists
    local info="$1"
    local path="$2"
    local fix_msg="$3"
    if [[ -e "$path"  ]]; then
        good_msg "${path} exists"
    else
        error_msg "${info} was not found at ${package}" "$fix_msg"
    fi
}

apt_installed() {
    local package="${1}"
    local installed=$(dpkg --get-selections | grep -v deinstall |grep ${package})
    local fix_msg="You can install this package by running the following command\n apt-get install ${package}"
    if [[ "${installed}" = ""  ]]; then
        error_msg "Apt package ${package} missing" "$fix_msg"
    else
        good_msg "Apt package ${package} found"
    fi
}

pip_installed() {
    local package="${1}"
    local installed=$(pip list \
                             | grep -E "^${package}\s\([0-9\.]*\)$" \
                             | grep -o "${package}")
    local fix_msg="You can install this package by running the following command\n pip install ${package}"
    if [[ "${installed}" = ""  ]]; then
        error_msg "Pip package ${package} missing" "$fix_msg"
    else
        good_msg "Pip package ${package} found"
    fi
}

good_msg() {
    if [[ ${PRINT_GOOD} = true ]]; then
        printf "\e[32mGood:\e[0m ${1}\n"
    fi
}

error_msg() {
    printf "\e[31mError:\e[0m ${1}\n"
    printf "$2 \n"
}

cleanup() {
    # put cleanup needs here
    exit 0
}

trap 'cleanup' EXIT

PRINT_GOOD=""

while getopts "vd" opt; do
    case $opt in
        v)
            PRINT_GOOD=true
            echo "Verbose mode activated" >&2
        ;;
        d)
            set -x
            PRINT_GOOD=true
            echo "Debug mode activated" >&2
        ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
        ;;
    esac
done

main