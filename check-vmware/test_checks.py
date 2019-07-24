import pytest
import random
import yaml

from pyVmomi import vim
from vmware_checks import CHECKS
from vmware_logconf import get_logger
from wrapanapi.systems.virtualcenter import VMWareSystem


@pytest.fixture(scope="session")
def provider_data():
    try:
        with open("conf/cfme-qe-yamls/complete/cfme_data.yaml", "r") as stream:
            cfme_data = yaml.safe_load(stream)
    except IOError:
        pytest.fail("CFME Data YAML file not found, no provider data available.")
    else:
        providers = cfme_data.get("management_systems")
        vsphere_providers = {
            key: providers[key] for key in list(providers.keys())
            if providers[key].get("type") == "virtualcenter"
        }
        yield vsphere_providers.get(random.choice(list(vsphere_providers.keys())))

@pytest.fixture(scope="session")
def credentials(provider_data):
    try:
        with open("conf/cfme-qe-yamls/complete/credentials.yaml", "r") as stream:
            creds = yaml.safe_load(stream)
            yield creds.get(provider_data.get("credentials"))
    except IOError:
        pytest.fail("Credential YAML file not found or not decrypted!")


@pytest.mark.parametrize("measurement", list(CHECKS.keys()))
def test_checks(provider_data, credentials, measurement):
    # get the necessary config
    if measurement == "system_ping_vms":
        # this test is very slow at present, and not used in shinken pack, so skip
        pytest.skip("Measurement {} is unused, so skipping".format(measurement))
    measure_func = CHECKS[measurement]
    hostname = provider_data.get("hostname")
    username, password = credentials.get("username"), credentials.get("password")
    logger = get_logger(True)

    # get the host if necessary
    is_host_check = "host" in measure_func.__code__.co_varnames
    host = None
    if is_host_check:
        # get the first host
        host = provider_data.get("hosts")[0].get("name")

    system = VMWareSystem(hostname, username, password)
    if host:
        host = system.get_obj(vim.HostSystem, host)

    # now try run the check
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        measure_func(host or system, logger=logger)
    assert pytest_wrapped_e.type == SystemExit
