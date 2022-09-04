"""Provides an implementation of ActiveClients port for a Meraki powered network."""
import logging
from typing import List
import meraki
from netorg_core import ports

class ActiveClientsAdapter(ports.ActiveClientsPort):
    """Provides an implementation of ActiveClients port for a Meraki powered network."""
    # pylint: disable=too-few-public-methods

    def __init__(self, config: dict) -> None:
        self.__logger = logging.getLogger("netorg")
        supress_logging = True
        if self.__logger.getEffectiveLevel() == logging.DEBUG:
            supress_logging = False
        self.dashboard = meraki.DashboardAPI(config['api_key'], suppress_logging=supress_logging)
        self.serial_id = config['serial_id']
        self.vlan_id   = str(config['vlan_id'])

    # overriding abstract method
    def load(self) -> List[ports.ActiveClient]:
        list_of_active_clients: List[ports.ActiveClient] = []
        device_clients = self.dashboard.devices.getDeviceClients(self.serial_id)
        # pylint: disable=line-too-long
        filtered_for_vlan = [ device_client for device_client in device_clients if str(device_client['vlan']) == self.vlan_id]
        for device_client in filtered_for_vlan:
            active_client = ports.ActiveClient(
                mac=device_client['mac'],
                #name=device_client['dhcpHostname'], # Is this used?
                name=device_client['description'],
                ip_address=device_client['ip']
            )
            list_of_active_clients.append(active_client)
        self.__logger.debug(f"ActiveClientsMerakiAdapter.load() returned {len(list_of_active_clients)} active clients")
        return list_of_active_clients
