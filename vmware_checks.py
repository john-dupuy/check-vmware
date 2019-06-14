#!/usr/bin/env python
# coding: utf-8
"""
These are the functions to check vmware hosts through the
vcenter API.
Checks against a host begin with "check_host"
Checks against vcenter begin with "check_system"
"""
import subprocess
import sys

from vmware_logconf import logger
from pyVmomi import vim

#----------------------------- HOST LEVEL CHECKS -----------------------------------------------#
def check_host_overall_status(host, **kwargs):
    """ Check overall host status. """
    status = host.overallStatus
    # determine ok, warning, critical, unknown state
    if status == "green":
        msg = "Ok: overall status of host {} is {}".format(host.name, status)
        logger.info(msg)
        print(msg)
        sys.exit(0)
    elif status == "yellow":
        msg = "Warning: esxi host {} may have a problem.".format(host.name)
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif status == "red":
        msg = "Critical: esxi host {} definitely has a problem".format(host.name)
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        msg = "Unknown: status of esxi host {} is unknown".format(host.name)
        logger.info(msg)
        print(msg)
        sys.exit(3)


def check_host_cpu_usage(host, warn=0.75, crit=0.9, **kwargs):
    warn = float(warn)
    crit = float(crit)

    cpu_usage = float(host.summary.quickStats.overallCpuUsage)
    cpu_total = float((host.hardware.cpuInfo.hz / 1024 / 1024) * host.hardware.cpuInfo.numCpuCores)

    cpu_frac = round(cpu_usage / cpu_total, 3)
    cpu_pct = cpu_frac * 100

    if cpu_frac < warn:
        msg = "Ok: cpu usage is {}%.".format(cpu_pct)
        print(msg)
        logger.info(msg)
        sys.exit(0)
    elif cpu_frac < crit:
        msg = "Warning: cpu usage is {}% ".format(cpu_pct)
        print(msg)
        logger.warning(msg)
        sys.exit(1)
    elif cpu_frac > crit:
        msg = ("Critical: cpu usage is {}%".format(cpu_pct))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    else:
        msg = ("Unknown: cpu usage is unknown on host {}".format(host.name))
        print(msg)
        logger.info(msg)
        sys.exit(3)


def check_host_datastore_accessibility(host, **kwargs):
    """ Check that the datastores are accessible to the host. This check has only two states"""
    okay, critical, all = [], [], []
    datastores = host.datastore
    for datastore in datastores:
        accessible = datastore.summary.accessible
        if accessible:
            okay.append((datastore.name, "accessible"))
        else:
            critical.append((datastore.name, "inaccessible"))
        all.append((datastore.name, "accessible" if accessible else "inaccessible"))
    if critical:
        msg = ("Critical: The following datastores are inaccessible: {}".format(critical))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    else:
        msg = ("Okay: All datastores connected to this host are accessible")
        print(msg)
        logger.info(msg)
        sys.exit(0)


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
        msg = ("Critical: the following datastore(s) definitely have an issue: {}\n "
               "Status of all datastores is: {}".format(critical, all))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: the following datastore(s) may have an issue: {}\n "
               "Status of all datastores is: {}".format(warning, all))
        print(msg)
        logger.warning(msg)
        sys.exit(1)
    elif unknown:
        msg = ("Unknown: the following datastore(s) are in an unknown state: {}\n"
               "Status of all datastores is: {}".format(unknown, all))
        print(msg)
        logger.info(msg)
        sys.exit(3)
    else:
        msg = ("Ok: all datastore(s) are in the green state: {}".format(okay))
        print(msg)
        logger.info(msg)
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
        msg = ("Critical: the following datastore(s) are in critical usage: {}\n "
               "Usage of all datastores is: {}".format(critical, all))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: the following datastore(s) have high usage: {}\n "
               "Usage of all datastores is: {}".format(warning, all))
        print(msg)
        logger.warning(msg)
        sys.exit(1)
    elif unknown:
        msg = ("Unknown: the following datastore(s) have unknown usage: {}\n"
               "Usage of all datastores is: {}".format(unknown, all))
        print(msg)
        logger.info(msg)
        sys.exit(3)
    else:
        msg = ("Ok: all datastore(s) have ample space: {}".format(okay))
        print(msg)
        logger.info(msg)
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
        msg = ("Ok: memory usage is {}%.".format(mem_pct))
        print(msg)
        logger.info(msg)
        sys.exit(0)
    elif mem_frac < crit:
        msg = ("Warning: memory usage is {}% ".format(mem_pct))
        print(msg)
        logger.warning(msg)
        sys.exit(1)
    elif mem_frac > crit:
        msg = ("Critical: memory usage is {}%".format(mem_pct))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    else:
        msg = ("Unknown: memory usage is unknown on host {}".format(host.name))
        print(msg)
        logger.info(msg)
        sys.exit(3)


#--------------- SYSTEM LEVEL CHECKS -------------------------------------------------------#
def check_system_datastore_status(system, **kwargs):
    """ Check the status of all the datastores on vcenter. """
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
        msg = ("Critical: the following datastore(s) definitely have an issue: {}\n "
               "Status of all datastores is: {}".format(critical, all))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: the following datastore(s) may have an issue: {}\n "
               "Status of all datastores is: {}".format(warning, all))
        print(msg)
        logger.warning(msg)
        sys.exit(1)
    elif unknown:
        msg = ("Unknown: the following datastore(s) are in an unknown state: {}\n"
               "Status of all datastores is: {}".format(unknown, all))
        print(msg)
        logger.info(msg)
        sys.exit(3)
    else:
        msg = ("Ok: all datastore(s) are in the green state: {}".format(okay))
        print(msg)
        logger.info(msg)
        sys.exit(0)


def check_system_datastore_usage(system, warn=0.75, crit=0.9, **kwargs):
    """ Check the usage of all the datastores on vcenter. """
    warn = float(warn)
    crit = float(crit)

    okay, warning, critical, unknown, all = [], [], [], [], []
    datastores = [
        system.get_obj(vim.Datastore, datastore) for datastore in system.list_datastore()
    ]

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
        msg = ("Critical: the following datastore(s) are in critical usage: {}\n "
               "Usage of all datastores is: {}".format(critical, all))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: the following datastore(s) have high usage: {}\n "
               "Usage of all datastores is: {}".format(warning, all))
        print(msg)
        logger.warning(msg)
        sys.exit(1)
    elif unknown:
        msg = ("Unknown: the following datastore(s) have unknown usage: {}\n"
               "Usage of all datastores is: {}".format(unknown, all))
        print(msg)
        logger.info(msg)
        sys.exit(3)
    else:
        msg = "Ok: all datastore(s) have ample space: {}".format(okay)
        print(msg)
        logger.info(msg)
        sys.exit(0)


def check_system_ping_vms(system, **kwargs):
    """ This checks the ping of all running VMs, no warning state for this check"""
    vms = system.list_vms()

    okay, critical, all = [], [], []
    for vm in vms:
        if vm.state == "VmState.RUNNING" and vm.ip:
            status = test_ping(vm.ip)
            if status == "Up":
                okay.append((vm.name, vm.ip, status))
            else:
                critical.append((vm.name, vm.ip, status))
            all.append((vm.name, vm.ip, status))

    if critical:
        msg = ("Critical: the following VMs are inaccessible: {}".format(critical))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    else:
        msg = "Okay: all running VMs that have IPs are accessible"
        print(msg)
        logger.info(msg)
        sys.exit(0)


def check_system_connection_vms(system, **kwargs):
    """ This checks the connection of all running VMs, no warning state for this check. This
        check will report if VMs are disconnected, inaccessible, invalid or orphaned. All of
        which will return a critical status. """
    vms = system.get_obj_list(vim.VirtualMachine)

    okay, critical, all = [], [], []
    for vm in vms:
        status = vm.summary.runtime.connectionState
        if status == "connected":
            okay.append((vm.name, status))
        else:
            critical.append((vm.name, status))
        all.append((vm.name, status))

    if critical:
        msg = ("Critical: the following VMs are not connected: {}".format(critical))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    else:
        msg = "Okay: all VMs are connected"
        print(msg)
        logger.info(msg)
        sys.exit(0)


def check_system_network_accessibility(system, **kwargs):
    """ Check that the network(s) is(are) accessible """
    okay, critical, all = [], [], []

    networks = system.get_obj_list(vim.Network)
    for network in networks:
        accessible = network.summary.accessible
        if accessible:
            okay.append((network.name, "accessible"))
        else:
            critical.append((network.name, "inaccessible"))
        all.append((network.name, "accessible" if accessible else "inaccessible"))
    if critical:
        msg = ("Critical: The following networks are inaccessible: {}".format(critical))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    else:
        msg = "Okay: All networks defined on this vcenter are accessible"
        print(msg)
        logger.info(msg)
        sys.exit(0)


def check_system_recent_tasks(system, warn=7, crit=15, **kwargs):
    warn, crit = int(warn), int(crit)
    # initialize empty list of tasks that have thrown an error
    error = []
    # get recent system tasks (recentTask gets all tasks from 10 min - Present)
    tasks = system.service_instance.content.taskManager.recentTask

    for task in tasks:
        if task.info.error:
            try:
                # not all tasks have a faultMessage
                error_info = getattr(
                    getattr(task.info.error, "faultMessage", [None])[0], "message", ""
                )
            except Exception:
                error_info = getattr(task.info, "msg", "")

            error.append((
                getattr(task.info, "descriptionId", ""),
                getattr(task.info, "state", ""),
                getattr(task.info, "entityName", ""),
                error_info,
                task.info.completeTime.isoformat()
            ))

    if len(error) > crit:
        msg = ("Critical: More than {} tasks have errors: \n {}".format(crit, error))
        print(msg)
        logger.error(msg)
        sys.exit(2)
    elif len(error) > warn:
        msg = ("Warning: More than {} tasks have errors: \n {}".format(warn, error))
        print(msg)
        logger.warning(msg)
        sys.exit(1)
    else:
        msg = "Okay: Less than {} tasks in past 10 minutes completed without error".format(warn)
        print(msg)
        logger.info(msg)
        sys.exit(0)


#----------- UTILITY FUNCTION ---------------------------------------------#
def test_ping(ip):
    # TODO: faster implementation of this?
    pingstatus = "Up"
    try:
        subprocess.check_output(
            "ping -c 1 -W 4 {}".format(ip),
            shell=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        pingstatus = "Down"
    return pingstatus


CHECKS = {
    "host_status": check_host_overall_status,
    "host_cpu": check_host_cpu_usage,
    "host_memory": check_host_memory_usage,
    "host_datastore_accessibility": check_host_datastore_accessibility,
    "host_datastore_status": check_host_datastore_status,
    "host_datastore_usage": check_host_datastore_usage,
    "system_datastore_status": check_system_datastore_status,
    "system_datastore_usage": check_system_datastore_usage,
    "system_ping_vms": check_system_ping_vms,
    "system_connection_vms": check_system_connection_vms,
    "system_network_accessibility": check_system_network_accessibility,
    "system_tasks": check_system_recent_tasks,
}
