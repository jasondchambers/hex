"""Tests for organize.py."""
import unittest
from typing import List
from adapters import fixedipreservations_meraki
from netorg_core import devicetable
from netorg_core import devicetableloader
from netorg_core import ports

class KnownDevicesTestAdapter(ports.KnownDevicesPort):
    """Test data for fixed IP reservations."""

    list_of_known_devices: List[ports.KnownDevice] = []

    # overriding abstract method
    def load(self) -> List[ports.KnownDevice]:
        return self.list_of_known_devices

    # overriding abstract method
    def save(self,device_table: devicetable.DeviceTable) -> None:
        pass

    @staticmethod
    def get_list_of_macs() :
        """Return list of MACs."""
        return [d.mac for d in KnownDevicesTestAdapter.list_of_known_devices]

class ActiveClientsTestAdapter(ports.ActiveClientsPort):
    """Test data for active clients."""

    list_of_active_clients: List[ports.ActiveClient] = [
        ports.ActiveClient(mac='__a_201', name='__a_201', ip_address='192.168.128.201'),
        ports.ActiveClient(mac='__a_202', name='__a_202', ip_address='192.168.128.202')
    ]

    # overriding abstract method
    def load(self) -> List[ports.ActiveClient]:
        return self.list_of_active_clients

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in ActiveClientsTestAdapter.list_of_active_clients]

class FixedIpReservationsTestAdapter(ports.FixedIpReservationsPort):
    """Test data for fixed IP reservations."""

    list_of_fixed_ip_reservations: List[ports.FixedIpReservation] = [
        ports.FixedIpReservation(mac='_r__203', ip_address='192.168.128.203', name='_r__203') # Expect this to be skipped because it is not known and not active
    ]

    # overriding abstract method
    def load(self) -> List[ports.FixedIpReservation]: 
        return self.list_of_fixed_ip_reservations

    # overriding abstract method
    def save(self,device_table: devicetable.DeviceTable) -> None: 
        pass

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in FixedIpReservationsTestAdapter.list_of_fixed_ip_reservations]

class TestFixedIpReservationsMerakiAdapter(unittest.TestCase) :
    """Tests for organizing the network."""

    def test_generate_ip_reservations(self):
        """Test FixedIpReservationsMerakiAdapter.__generate_fixed_ip_reservations()."""
        device_table_loader = devicetableloader.DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        device_table = device_table_loader.load_all()
        fixed_ip_reservations = fixedipreservations_meraki.FixedIpReservationsAdapter._FixedIpReservationsAdapter__generate_fixed_ip_reservations(device_table)
        self.assertEqual(len(fixed_ip_reservations), 2, "Expected there to be 2 reservations")
        self.assertEqual(fixed_ip_reservations['__a_201']['ip'], '192.168.128.201')
        self.assertEqual(fixed_ip_reservations['__a_202']['ip'], '192.168.128.202')