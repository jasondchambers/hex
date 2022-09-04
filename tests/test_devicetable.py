from typing import List
import unittest
from netorg_core import devicetable
from netorg_core import devicetableloader
#from devicetableloader import DeviceTableLoader
from netorg_core import ports
#from ports import ActiveClient, ActiveClientsPort, FixedIpReservation, FixedIpReservationsPort, KnownDevice, KnownDevicesPort

# Test table
#
#   known | reserved (IP) | active | Description                | Action
# ==============+===============+========+======================+=======
#       0 |             0 |      0 |                            |
# aab   0 |             0 |      1 | active                     | register the device
# aba   0 |             1 |      0 | reserved                   | remove reservation
# abb   0 |             1 |      1 | reserved & active          | register the device
# baa   1 |             0 |      0 | known                      | create reservation
# bab   1 |             0 |      1 | known & active             | convert to static reservation
# bba   1 |             1 |      0 | known & reserved           |
# bbb   1 |             1 |      1 | known & reserved & active  |
TEST_TABLE_SIZE = 7

class KnownDevicesTestAdapter(ports.KnownDevicesPort):
    """Load known devices for test purporses."""

    list_of_known_devices: List[ports.KnownDevice] = [
        ports.KnownDevice(name='Meerkat',         mac='baa', group='servers'),
        ports.KnownDevice(name='Office Printer',  mac='bab', group='printers'),
        ports.KnownDevice(name='Front Doorbell',  mac='bba', group='security'),
        ports.KnownDevice(name='Driveway camera', mac='bbb', group='security')
    ]

    # overriding abstract method
    def load(self) -> List[ports.KnownDevice]:
        return self.list_of_known_devices

    # overriding abstract method
    def save(self,device_table: devicetable.DeviceTable) -> None:
        pass

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in KnownDevicesTestAdapter.list_of_known_devices]

class ActiveClientsTestAdapter(ports.ActiveClientsPort):

    list_of_active_clients: List[ports.ActiveClient] = [
        ports.ActiveClient(mac='aab', name='HS105',           ip_address='192.168.128.201'),
        ports.ActiveClient(mac='abb', name='HS105',           ip_address='192.168.128.202'),
        ports.ActiveClient(mac='bab', name='Office Printer',  ip_address='192.168.128.203'),
        ports.ActiveClient(mac='bbb', name='Driveway camera', ip_address='192.168.128.204')
    ]

    # overriding abstract method
    def load(self) -> List[ports.ActiveClient]:
        return self.list_of_active_clients

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in ActiveClientsTestAdapter.list_of_active_clients]

class FixedIpReservationsTestAdapter(ports.FixedIpReservationsPort):

    list_of_fixed_ip_reservations: List[ports.FixedIpReservation] = [
        ports.FixedIpReservation(mac='aba', ip_address='192.168.128.191', name='Work Laptop'),
        ports.FixedIpReservation(mac='abb', ip_address='192.168.128.202', name='HS105'),
        ports.FixedIpReservation(mac='bba', ip_address='192.168.128.191', name='Echo 1'),
        ports.FixedIpReservation(mac='bbb', ip_address='192.168.128.204', name='Echo 2')
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

class TestDeviceTableLoader(unittest.TestCase) :
    """Test cases for DeviceTableLoader."""

    def test_load_known(self) :
        """Test loading of known devices."""
        device_table_loader = devicetableloader.DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=None,
            fixed_ip_reservations_port=None
        )
        device_table_loader._DeviceTableLoader__load_known()
        df = device_table_loader.device_table_builder.build().get_df()
        self.assertEqual(len(KnownDevicesTestAdapter.list_of_known_devices),df.query("known").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_active(self) :
        """Test loading of active devices."""
        device_table_loader = devicetableloader.DeviceTableLoader(
            known_devices_port=None,
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=None
        )
        device_table_loader._DeviceTableLoader__load_active_clients()
        df = device_table_loader.device_table_builder.build().get_df()
        self.assertEqual(0,df.query("known").shape[0])
        self.assertEqual(len(ActiveClientsTestAdapter.list_of_active_clients),df.query("active").shape[0])
        self.assertEqual(0,df.query("reserved").shape[0])

    def test_load_fixed_ip_reservations(self) :
        """Test loading of fixed IP reservations."""
        device_table_loader = devicetableloader.DeviceTableLoader(
            known_devices_port=None,
            active_clients_port=None,
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        device_table_loader._DeviceTableLoader__load_fixed_ip_reservations()
        df = device_table_loader.device_table_builder.build().get_df()
        self.assertEqual(0,df.query("known").shape[0])
        self.assertEqual(0,df.query("active").shape[0])
        self.assertEqual(len(FixedIpReservationsTestAdapter.list_of_fixed_ip_reservations),df.query("reserved").shape[0])

    def test_load_all(self) :
        """Test loading of all data."""
        device_table_loader = devicetableloader.DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        df = device_table_loader.load_all().get_df()
        self.assertEqual(TEST_TABLE_SIZE,df.shape[0])

        # known
        self.assertEqual(len(KnownDevicesTestAdapter.list_of_known_devices),df.query("known").shape[0])
        for mac in KnownDevicesTestAdapter.get_list_of_macs() :
            self.assertIn(mac,df.query("known")["mac"].tolist())

        # active
        self.assertEqual(len(ActiveClientsTestAdapter.list_of_active_clients),df.query("active").shape[0])
        for mac in ActiveClientsTestAdapter.get_list_of_macs() :
            self.assertIn(mac,df.query("active")["mac"].tolist())

        # reserved
        self.assertEqual(len(FixedIpReservationsTestAdapter.list_of_fixed_ip_reservations),df.query("reserved").shape[0])
        for mac in FixedIpReservationsTestAdapter.get_list_of_macs() :
            self.assertIn(mac,df.query("reserved")["mac"].tolist())

        ## known and active
        known_set = set(KnownDevicesTestAdapter.get_list_of_macs())
        active_set = set(ActiveClientsTestAdapter.get_list_of_macs())
        expected = known_set.intersection(active_set)
        actual = df.query("known and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # known and reserved
        reserved_set = set(FixedIpReservationsTestAdapter.get_list_of_macs())
        expected = known_set.intersection(reserved_set)
        actual = df.query("known and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # active and reserved
        expected = active_set.intersection(reserved_set)
        actual = df.query("active and reserved")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))

        # known and reserved and active
        expected = known_set.intersection(reserved_set,active_set)
        actual = df.query("known and reserved and active")["mac"].tolist()
        for mac in expected :
            self.assertIn(mac,actual)
        self.assertEqual(len(expected),len(actual))
