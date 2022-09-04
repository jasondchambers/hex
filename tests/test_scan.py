"""Tests for scan.py."""
import unittest
from typing import List
from netorg_core import devicetable
from netorg_core import devicetableloader
from netorg_core import ports
from netorg_core import scan

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

class KnownDevicesTestAdapter(ports.KnownDevicesPort):
    """Test data for known devices."""

    list_of_known_devices: List[ports.KnownDevice] = [
        ports.KnownDevice(name='k__', mac='k__', group='servers'),
        ports.KnownDevice(name='k_a', mac='k_a', group='printers'),
        ports.KnownDevice(name='kr_', mac='kr_', group='security'),
        ports.KnownDevice(name='kra', mac='kra', group='unclassified')
    ]

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
        ports.ActiveClient(mac='__a', name='__a', ip_address='192.168.128.201'),
        ports.ActiveClient(mac='_ra', name='_ra', ip_address='192.168.128.203'),
        ports.ActiveClient(mac='k_a', name='k_a', ip_address='192.168.128.205'),
        ports.ActiveClient(mac='kra', name='kra', ip_address='192.168.128.207')
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
        ports.FixedIpReservation(mac='_r_', ip_address='192.168.128.202', name='_r_'),
        ports.FixedIpReservation(mac='_ra', ip_address='192.168.128.203', name='_ra'),
        ports.FixedIpReservation(mac='kr_', ip_address='192.168.128.206', name='kr_'),
        ports.FixedIpReservation(mac='kra', ip_address='192.168.128.207', name='kra')
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

class TestNetorgScanner(unittest.TestCase) :
    """Tests for NetorgScanner."""

    def test_run(self):
        """Test NetorgScanner.run()."""
        device_table_loader = devicetableloader.DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        device_table = device_table_loader.load_all()
        scanner = scan.NetorgScanner(device_table)
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
