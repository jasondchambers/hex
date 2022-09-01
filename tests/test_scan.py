"""Tests for scan.py."""
import unittest
from typing import List
from devicetable import DeviceTable
from devicetableloader import DeviceTableLoader
from ports import ActiveClient, ActiveClientsPort, FixedIpReservation, FixedIpReservationsPort, KnownDevice, KnownDevicesPort
from scan import NetorgScanner

# pylint: disable=line-too-long
# Test table
#
#   known | reserved (IP) | IP   | active | Description                                | Action
# ========+===============+======+========+===========================================+=======
#       0 |             0 |      |      0 |                                            |
# __a   0 |             0 | .201 |      1 | active                                     | register the device
# _r_   0 |             1 | .202 |      0 | reserved                                   | remove reservation
# _ra   0 |             1 | .203 |      1 | reserved & active                          | register the device
# k__   1 |             0 |      |      0 | known                                      | create reservation
# k_a   1 |             0 | .205 |      1 | known & active                             | convert to static reservation
# kr_   1 |             1 | .206 |      0 | known & reserved                           |
# kra   1 |             1 | .207 |      1 | known & reserved & active (& unclassified) | invite classification

class KnownDevicesTestAdapter(KnownDevicesPort):
    """Test data for known devices."""

    list_of_known_devices: List[KnownDevice] = [
        KnownDevice(name='k__', mac='k__', group='servers'),
        KnownDevice(name='k_a', mac='k_a', group='printers'),
        KnownDevice(name='kr_', mac='kr_', group='security'),
        KnownDevice(name='kra', mac='kra', group='unclassified')
    ]

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
        ActiveClient(mac='__a', name='__a', ip_address='192.168.128.201'),
        ActiveClient(mac='_ra', name='_ra', ip_address='192.168.128.203'),
        ActiveClient(mac='k_a', name='k_a', ip_address='192.168.128.205'),
        ActiveClient(mac='kra', name='kra', ip_address='192.168.128.207')
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
        FixedIpReservation(mac='_r_', ip_address='192.168.128.202', name='_r_'),
        FixedIpReservation(mac='_ra', ip_address='192.168.128.203', name='_ra'),
        FixedIpReservation(mac='kr_', ip_address='192.168.128.206', name='kr_'),
        FixedIpReservation(mac='kra', ip_address='192.168.128.207', name='kra')
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

class TestNetorgScanner(unittest.TestCase) :
    """Tests for NetorgScanner."""

    def test_run(self):
        """Test NetorgScanner.run()."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        device_table = device_table_loader.load_all()
        scanner = NetorgScanner(device_table)
        scanner.run()
        analysis = scanner.analysis
        self.assertListEqual(analysis['not_known_not_reserved_ACTIVE']['device_names'], ['__a'])
        self.assertListEqual(analysis['not_known_RESERVED_not_active']['device_names'], ['_r_'])
        self.assertListEqual(analysis['not_known_RESERVED_ACTIVE']['device_names'], ['_ra'])
        self.assertListEqual(analysis['KNOWN_not_reserved_not_active']['device_names'], ['k__'])
        self.assertListEqual(analysis['KNOWN_RESERVED_not_active']['device_names'], ['kr_'])
        self.assertListEqual(analysis['KNOWN_RESERVED_ACTIVE']['device_names'], ['kra'])
        actual = analysis['ACTIVE_UNCLASSIFIED']['device_names']
        actual.sort()
        expected = ['__a', '_ra', 'kra']
        expected.sort()
        self.assertListEqual(actual, expected)
