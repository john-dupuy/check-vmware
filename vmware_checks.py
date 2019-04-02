#!/usr/bin/env python
# coding: utf-8
"""
These are the functions to check vmware hosts through the
vcenter API.
Checks against a host begin with "check_host"
Checks against vcenter begin with "check_system"
"""
import sys

from pyVmomi import vim

def check_host_overall_status(host, **kwargs):
    """ Check overall host status. """
    status = host.overallStatus
    # determine ok, warning, critical, unknown state
    if status == "green":
        print("Ok: overall status of host {} is {}".format(host.name, status))
        sys.exit(0)
    elif status == "yellow":
        print("Warning: esxi host {} may have a problem.".format(host.name))
        sys.exit(1)
    elif status == "red":
        print("Critical: esxi host {} definitely has a problem".format(host.name))
        sys.exit(2)
    else:
        print("Unknown: status of esxi host {} is unknown".format(host.name))
        sys.exit(3)


def check_host_cpu_usage(host, warn=0.75, crit=0.9, **kwargs):
    warn = float(warn)
    crit = float(crit)

    cpu_usage = float(host.summary.quickStats.overallCpuUsage)
    cpu_total = float((host.hardware.cpuInfo.hz / 1024 / 1024) * host.hardware.cpuInfo.numCpuCores)

    cpu_frac = round(cpu_usage / cpu_total, 3)
    cpu_pct = cpu_frac * 100

    if cpu_frac < warn:
        print("Ok: cpu usage is {}%.".format(cpu_pct))
        sys.exit(0)
    elif cpu_frac < crit:
        print("Warning: cpu usage is {}% ".format(cpu_pct))
        sys.exit(1)
    elif cpu_frac > crit:
        print("Critical: cpu usage is {}%".format(cpu_pct))
        sys.exit(2)
    else:
        print("Unknown: cpu usage is unknown on host {}".format(host.name))
        sys.exit(3)


def check_host_datastore_status(host, **kwargs):
    """ Check the status of all the datastores on the host. """
    okay, warning, critical, unknown, all = [], [], [], [], []
    datastores = host.datastore
    for datastore in datastores:
        status = datastore.overallStatus
        if status == "green":
            okay.append((datastore.name, status))
        elif status == "yellow":
            warning.append((datastore.name, status))
        elif status == "red":
            critical.append((datastore.name, status))
        else:
            unknown.append((datastore.name, status))
        all.append((datastore.name, status))

    if critical:
        print("Critical: the following datastore(s) definitely have an issue: {}\n "
              "Status of all datastores is: {}".format(critical, all))
        sys.exit(2)
    elif warning:
        print("Warning: the following datastore(s) may have an issue: {}\n "
              "Status of all datastores is: {}".format(warning, all))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following datastore(s) are in an unknown state: {}\n"
              "Status of all datastores is: {}".format(unknown, all))
        sys.exit(3)
    else:
        print("Ok: all datastore(s) are in the green state: {}".format(okay))
        sys.exit(0)


def check_host_datastore_usage(host, warn=0.75, crit=0.9, **kwargs):
    """ Check the usage of all the datastores on the host. """
    warn = float(warn)
    crit = float(crit)
    okay, warning, critical, unknown, all = [], [], [], [], []

    datastores = host.datastore
    for datastore in datastores:
        freespace = float(datastore.summary.freeSpace)
        totalspace = float(datastore.summary.capacity)

        usage = round(1 - (freespace / totalspace), 3)
        pct = str(usage * 100) + "%"
        if usage < warn:
            okay.append((datastore.name, pct))
        elif usage < crit:
            warning.append((datastore.name, pct))
        elif usage > crit:
            critical.append((datastore.name, pct))
        else:
            unknown.append((datastore.name, pct))
        all.append((datastore.name, pct))

    if critical:
        print("Critical: the following datastore(s) are in critical usage: {}\n "
              "Usage of all datastores is: {}".format(critical, all))
        sys.exit(2)
    elif warning:
        print("Warning: the following datastore(s) have high usage: {}\n "
              "Usage of all datastores is: {}".format(warning, all))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following datastore(s) have unknown usage: {}\n"
              "Usage of all datastores is: {}".format(unknown, all))
        sys.exit(3)
    else:
        print("Ok: all datastore(s) have ample space: {}".format(okay))
        sys.exit(0)


def check_host_memory_usage(host, warn=0.75, crit=0.9, **kwargs):
    """ Check memory usage of the host. """
    warn = float(warn)
    crit = float(crit)

    mem_usage = float(host.summary.quickStats.overallMemoryUsage)
    mem_total = float(host.hardware.memorySize / 1024 / 1024)

    mem_frac = round(mem_usage / mem_total, 3)
    mem_pct = mem_frac * 100

    if mem_frac < warn:
        print("Ok: memory usage is {}%.".format(mem_pct))
        sys.exit(0)
    elif mem_frac < crit:
        print("Warning: memory usage is {}% ".format(mem_pct))
        sys.exit(1)
    elif mem_frac > crit:
        print("Critical: memory usage is {}%".format(mem_pct))
        sys.exit(2)
    else:
        print("Unknown: memory usage is unknown on host {}".format(host.name))
        sys.exit(3)


def check_system_datastore_status(system, **kwargs):
    """ Check the status of all the datastores on the host. """
    okay, warning, critical, unknown, all = [], [], [], [], []
    datastores = [
        system.get_obj(vim.Datastore, datastore) for datastore in system.list_datastore()
    ]
    for datastore in datastores:
        status = datastore.overallStatus
        if status == "green":
            okay.append((datastore.name, status))
        elif status == "yellow":
            warning.append((datastore.name, status))
        elif status == "red":
            critical.append((datastore.name, status))
        else:
            unknown.append((datastore.name, status))
        all.append((datastore.name, status))

    if critical:
        print("Critical: the following datastore(s) definitely have an issue: {}\n "
              "Status of all datastores is: {}".format(critical, all))
        sys.exit(2)
    elif warning:
        print("Warning: the following datastore(s) may have an issue: {}\n "
              "Status of all datastores is: {}".format(warning, all))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following datastore(s) are in an unknown state: {}\n"
              "Status of all datastores is: {}".format(unknown, all))
        sys.exit(3)
    else:
        print("Ok: all datastore(s) are in the green state: {}".format(okay))
        sys.exit(0)


CHECKS = {
    "host_status": check_host_overall_status,
    "host_cpu": check_host_cpu_usage,
    "host_memory": check_host_memory_usage,
    "host_datastore_status": check_host_datastore_status,
    "host_datastore_usage": check_host_datastore_usage,
    "system_datastore_status": check_system_datastore_status
}