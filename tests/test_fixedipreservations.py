"""Tests for organize.py."""
import unittest
from typing import List
from adapters.fixedipreservations_meraki import FixedIpReservationsMerakiAdapter
from devicetable import DeviceTable
from devicetableloader import DeviceTableLoader
from ports import ActiveClient, ActiveClientsPort, FixedIpReservation, FixedIpReservationsPort, KnownDevice, KnownDevicesPort

class KnownDevicesTestAdapter(KnownDevicesPort):
    """Test data for fixed IP reservations."""

    list_of_known_devices: List[KnownDevice] = []

    # overriding abstract method
    def load(self) -> List[KnownDevice]:
        return self.list_of_known_devices

    # overriding abstract method
    def save(self,device_table: DeviceTable) -> None:
        pass

    @staticmethod
    def get_list_of_macs() :
        """Return list of MACs."""
        return [d.mac for d in KnownDevicesTestAdapter.list_of_known_devices]

class ActiveClientsTestAdapter(ActiveClientsPort):
    """Test data for active clients."""

    list_of_active_clients: List[ActiveClient] = [
        ActiveClient(mac='__a_201', name=None, description='__a_201', ip_address='192.168.128.201'),
        ActiveClient(mac='__a_202', name=None, description='__a_202', ip_address='192.168.128.202')
    ]

    # overriding abstract method
    def load(self) -> List[ActiveClient]:
        return self.list_of_active_clients

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in ActiveClientsTestAdapter.list_of_active_clients]

class FixedIpReservationsTestAdapter(FixedIpReservationsPort):
    """Test data for fixed IP reservations."""

    list_of_fixed_ip_reservations: List[FixedIpReservation] = [
        FixedIpReservation(mac='_r__203', ip_address='192.168.128.203', name='_r__203') # Expect this to be skipped because it is not known and not active
    ]

    # overriding abstract method
    def load(self) -> List[FixedIpReservation]: 
        return self.list_of_fixed_ip_reservations

    # overriding abstract method
    def save(self,device_table: DeviceTable) -> None: 
        pass

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in FixedIpReservationsTestAdapter.list_of_fixed_ip_reservations]

class TestFixedIpReservationsMerakiAdapter(unittest.TestCase) :
    """Tests for organizing the network."""

    def test_generate_ip_reservations(self):
        """Test FixedIpReservationsMerakiAdapter.__generate_fixed_ip_reservations()."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        device_table = device_table_loader.load_all()
        fixed_ip_reservations = FixedIpReservationsMerakiAdapter._FixedIpReservationsMerakiAdapter__generate_fixed_ip_reservations(device_table)
        self.assertEqual(len(fixed_ip_reservations), 2, "Expected there to be 2 reservations")
        self.assertEqual(fixed_ip_reservations['__a_201']['ip'], '192.168.128.201')
        self.assertEqual(fixed_ip_reservations['__a_202']['ip'], '192.168.128.202')