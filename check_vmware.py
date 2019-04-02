# coding: utf-8
"""
This script performs checks for vmware hosts through the
vcenter API
"""

import argparse
import sys

from argparse import RawTextHelpFormatter
from vmware_checks import CHECKS
from wrapanapi.systems.virtualcenter import VMWareSystem
from pyVmomi import vim


def get_measurement(measurement):
    return CHECKS.get(measurement, None)


def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-V",
        "--vsphere",
        dest="vsphere",
        help="Hostname of vSphere client",
        type=str
    )
    parser.add_argument(
        "-H",
        "--hostname",
        dest="hostname",
        help="Hostname of vSphere esxi host",
        type=str,
    )
    parser.add_argument(
        "-u",
        "--user",
        dest="user",
        help="remote user to use",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        help="password for vSphere client",
        type=str
    )
    parser.add_argument(
        "-m",
        "--measurement",
        dest="measurement",
        help="Type of measurement to carry out",
        type=str
    )
    parser.add_argument(
        "-w",
        "--warning",
        dest="warning",
        help="Warning value for the check as a fraction. (e.g. 0.8)",
        default=0.75
    )
    parser.add_argument(
        "-c",
        "--critical",
        dest="critical",
        help="Critical value for the check as a fraction. (e.g. 0.9)",
        default=0.9
    )
    args = parser.parse_args()
    if float(args.warning) > float(args.critical):
        print("Error: warning value can not be greater than critical value")
        sys.exit(3)

    # connect to the system
    system = VMWareSystem(args.vsphere, args.user, args.password)
    # get the host object
    host = None
    if args.hostname:
        host = system.get_obj(vim.HostSystem, args.hostname)
        if not host:
            print("Error: esxi hostname {} does not exist on vSphere {}".format(
                args.hostname, args.vsphere
            ))
            sys.exit(3)
    # get measurement function
    measure_func = get_measurement(args.measurement)
    if not measure_func:
        print("Error: measurement {} not understood".format(args.measurement))
        sys.exit(3)
    # run the measurement function
    measure_func(host or system, warn=args.warning, crit=args.critical)


if __name__ == "__main__":
    main()

