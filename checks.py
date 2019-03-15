# coding: utf-8
"""
These are the functions to check vmware hosts through the
vcenter API
"""
import sys


def check_overall_status(host, **kwargs):
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


def check_cpu_usage(host, warn=0.75, crit=0.9, **kwargs):
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


def check_datastore_status(host, **kwargs):
    """ Check the connection of all the datastores on the host. """
    okay, warn, crit, unknown, all = [], [], [], [], []
    datastores = host.datastore
    for datastore in datastores:
        status = datastore.overallStatus
        if status == "green":
            okay.append((datastore.name, status))
        elif status == "yellow":
            warn.append((datastore.name, status))
        elif status == "red":
            crit.append((datastore.name, status))
        else:
            unknown.append((datastore.name, status))
        all.append((datastore.name, status))

    if crit:
        print("Critical: the following datastore(s) definitely have an issue: {}\n "
              "Status of all datastores is: {}".format(crit, all))
        sys.exit(2)
    elif warn:
        print("Warning: the following datastore(s) may have an issue: {}\n "
              "Status of all datastores is: {}".format(warn, all))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following datastore(s) are in an unknown state: {}\n"
              "Status of all datastores is: {}".format(unknown, all))
        sys.exit(3)
    else:
        print("Ok: all datastore(s) are in the green state: {}".format(okay))
        sys.exit(0)


def check_memory_usage(host, warn=0.75, crit=0.9, **kwargs):
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


CHECKS = {
    "status": check_overall_status,
    "cpu": check_cpu_usage,
    "memory": check_memory_usage,
    "datastore_status": check_datastore_status,
}