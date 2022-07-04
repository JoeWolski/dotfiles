#!/usr/bin/python3

import os
import subprocess
import sys

if not os.geteuid() == 0:
    sys.exit("Your must run as root")

if len(sys.argv) != 2:
    print("Use $sudo set-nvidia <on|off|status>")
    sys.exit(1)

action = sys.argv[1].lower()
assert action in ["on", "off", "status"], "argument should be one of on, off, status"


def load_driver():
    print("Trying to load the nvidia driver if needed: {}".format(
        subprocess.check_output("modprobe nvidia_uvm nvidia", shell=True).decode("utf-8")))


def unload_driver():
    print("Trying to unload the nvidia driver if needed: {}".format(
        subprocess.check_output("modprobe -r nvidia_uvm nvidia", shell=True).decode("utf-8")))


def bbswitch_is_loaded():
    return os.path.exists("/proc/acpi/bbswitch")


def load_bbswitch():
    return subprocess.run("modprobe bbswitch", shell=True).decode("utf-8")


def switch_gpu(status):
    assert status.lower() in ["on", "off"]
    command = "echo {} | tee /proc/acpi/bbswitch".format(action.upper())
    try:
        print("Trying to switch {} the GPU: {}".format(status,
                                                       subprocess.check_output(command, shell=True).decode("utf-8")))

    except subprocess.CalledProcessError:
        print("bbswitch was not loaded, loading it: {}".format(load_bbswitch()))

        print("Retrying to switch {} the GPU: {}".format(status,
                                                         subprocess.check_output(command, shell=True).decode("utf-8")))
        if action == "off":
            unload_driver()
            switch_gpu(action)
        elif action == "on":
            switch_gpu(action)
            load_driver()
        if not bbswitch_is_loaded():
            print("bbswitch was not loaded, loading it: {}".format(
                load_bbswitch()))
            print("GPU status: {}".format(
                subprocess.run(["cat", "/proc/acpi/bbswitch"], stdout=subprocess.PIPE).stdout.decode("utf-8")))
