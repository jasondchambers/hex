"""Test for ipv4privatenetworkspace."""
import unittest
from typing import List
from networkspace import NetworkIsOutOfSpace, NetworkMapper, Ipv4PrivateNetworkSpace
from devicetable import DeviceTable
from devicetableloader import DeviceTableLoader
from ports import ActiveClient, ActiveClientsPort, FixedIpReservation, FixedIpReservationsPort, KnownDevice, KnownDevicesPort

class TestIpv4PrivateNetworkSpace(unittest.TestCase):
    """Tests for Ipv4PrivateNetworkSpace."""

    def test_invalid_cidr(self) :
        """Test with an invalid CIDR."""
        self.assertRaises(ValueError, Ipv4PrivateNetworkSpace, "x.x.x.x")

    def test_cidr_has_host_bits_set(self) :
        """Test where the CIDR has the host bits set (i.e. non zero)."""
        self.assertRaises(ValueError, Ipv4PrivateNetworkSpace, "192.168.128.22/24")

    def test_public_cidr(self) :
        """Test with a public CIDR."""
        self.assertRaises(ValueError, Ipv4PrivateNetworkSpace, "8.0.0.0/8")

    def test_end_to_end(self) :
        """Test exhaustion of space."""
        # pylint: disable=line-too-long
        # pylint: disable=unused-variable
        network_space = Ipv4PrivateNetworkSpace("192.168.128.252/30")
        self.assertEqual(2,len(network_space.get_address_set()), "Expected address_set to be size 2")
        self.assertIn('192.168.128.253', network_space.get_address_set())
        self.assertIn('192.168.128.254', network_space.get_address_set())
        self.assertEqual(0, len(network_space.get_used_set()), "Expected used_set to be size 0")
        self.assertEqual(2, len(network_space.get_unused_set()), "Expected unused_set to be size 2")
        self.assertIn('192.168.128.253', network_space.get_unused_set(), "Expected unused_set to contain 192.168.128.253")
        self.assertIn('192.168.128.254', network_space.get_unused_set(), "Expected unused_set to contain 192.168.128.254")
        allocated_address = network_space.allocate_address()
        self.assertEqual(1, len(network_space.get_used_set()), "Expected used_set to be size 1")
        allocated_address = network_space.allocate_address()
        self.assertEqual(2, len(network_space.get_used_set()), "Expected used_set to be size 2")
        self.assertEqual(0, len(network_space.get_unused_set()), "Expected used_set to be size 0")
        self.assertRaises(NetworkIsOutOfSpace, network_space.allocate_address)

    def test_allocate_specific_address(self) :
        """Test allocation of a specific address."""
        # pylint: disable=line-too-long
        network_space = Ipv4PrivateNetworkSpace("192.168.128.252/30")
        self.assertRaises(ValueError, network_space.allocate_specific_address, "8.8.8.8") # Not in CIDR
        allocated_address = network_space.allocate_specific_address("192.168.128.254")
        self.assertEqual('192.168.128.254', allocated_address, "Expected allocate_address to return 192.168.128.254")
        self.assertRaises(ValueError, network_space.allocate_specific_address, "192.168.128.254") # Already in use

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

class KnownDevicesTestAdapterForOutOfSpaceTest(KnownDevicesPort):
    """Test data for known devices."""

    list_of_known_devices: List[KnownDevice] = [
        KnownDevice(name='k__', mac='k__', group='servers')
    ]

    # overriding abstract method
    def load(self) -> List[KnownDevice]:
        return self.list_of_known_devices

    # overriding abstract method
    def save(self,device_table: DeviceTable) -> None:
        pass

class ActiveClientsTestAdapterForOutOfSpaceTest(ActiveClientsPort):
    """Test data for active clients."""

    list_of_active_clients: List[ActiveClient] = [
        ActiveClient(mac='_ra', name='_ra', ip_address='192.168.128.254')
    ]

    # overriding abstract method
    def load(self) -> List[ActiveClient]:
        return self.list_of_active_clients

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in ActiveClientsTestAdapter.list_of_active_clients]

class FixedIpReservationsTestAdapterForOutOfSpaceTest(FixedIpReservationsPort):
    """Test data for fixed IP reservations."""

    list_of_fixed_ip_reservations: List[FixedIpReservation] = [
        FixedIpReservation(mac='_r_', ip_address='192.168.128.253', name='_r_')
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

class KnownDevicesTestAdapterForDuplicateIpTest(KnownDevicesPort):
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

class ActiveClientsTestAdapterForDuplicateIpTest(ActiveClientsPort):
    """Test data for active clients."""

    list_of_active_clients: List[ActiveClient] = [
        ActiveClient(mac='__a', name='__a', ip_address='192.168.128.201'),
        ActiveClient(mac='_ra', name='_ra', ip_address='192.168.128.203'),
        ActiveClient(mac='k_a', name='k_a', ip_address='192.168.128.205'),
        ActiveClient(mac='kra', name='kra', ip_address='192.168.128.202') # Duplicate IP with _r_
    ]

    # overriding abstract method
    def load(self) -> List[ActiveClient]:
        return self.list_of_active_clients

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in ActiveClientsTestAdapter.list_of_active_clients]

class FixedIpReservationsTestAdapterForDuplicateIpTest(FixedIpReservationsPort):
    """Test data for fixed IP reservations."""

    list_of_fixed_ip_reservations: List[FixedIpReservation] = [
        FixedIpReservation(mac='_r_', ip_address='192.168.128.202', name='_r_'),
        FixedIpReservation(mac='_ra', ip_address='192.168.128.203', name='_ra'),
        FixedIpReservation(mac='kr_', ip_address='192.168.128.206', name='kr_'),
        FixedIpReservation(mac='kra', ip_address='192.168.128.202', name='kra') # Duplicate IP with _r_
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

class KnownDevicesTestAdapterForIpReservationGeneratorTest(KnownDevicesPort):
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

class ActiveClientsTestAdapterForIpReservationGeneratorTest(ActiveClientsPort):
    """Test data for active clients."""

    list_of_active_clients: List[ActiveClient] = [
        ActiveClient(mac='__a_201', name='__a_201', ip_address='192.168.128.201'),
        ActiveClient(mac='__a_202', name='__a_202', ip_address='192.168.128.202')
    ]

    # overriding abstract method
    def load(self) -> List[ActiveClient]:
        return self.list_of_active_clients

    @staticmethod
    def get_list_of_macs() -> List[str]:
        """Return list of MACs."""
        return [d.mac for d in ActiveClientsTestAdapter.list_of_active_clients]

class FixedIpReservationsTestAdapterForIpReservationGeneratorTest(FixedIpReservationsPort):
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

class TestNetworkMapper(unittest.TestCase) :
    """Tests for organizing the network."""

    def test_organize(self):
        """Tests for NetworkMapper.map_to_network_space()."""
        # pylint: disable=unused-variable
        device_table_loader = DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        device_table = device_table_loader.load_all()
        devices_with_no_ip = device_table.get_df().query("ip == ''")['mac'].tolist()
        self.assertEqual(1, len(devices_with_no_ip), "Expected there to be one device needing an IP")
        network_mapper = NetworkMapper(vlan_subnet="192.168.128.0/24",device_table=device_table)
        network_mapper.map_to_network_space()
        devices_with_no_ip = device_table.get_df().query("ip == ''")['mac'].tolist()
        self.assertEqual(0, len(devices_with_no_ip), "Expected there to be zero devices needing an IP")

    def test_invalid_subnet(self):
        """Test NetworkMapper.map_to_network_space() where the device IPs are in a different subnet."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapter(),
            active_clients_port=ActiveClientsTestAdapter(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapter()
        )
        device_table = device_table_loader.load_all()
        network_mapper = NetworkMapper(
            vlan_subnet="192.168.128.252/30",# Different subnet to the IPs in the test data
            device_table=device_table)
        self.assertRaises(ValueError, network_mapper.map_to_network_space)

    def test_not_enough_network_space(self) :
        """Test NetworkMapper.map_to_network_space() where the network space is exhausted."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapterForOutOfSpaceTest(),
            active_clients_port=ActiveClientsTestAdapterForOutOfSpaceTest(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapterForOutOfSpaceTest()
        )
        device_table = device_table_loader.load_all()
        network_mapper = NetworkMapper(
            vlan_subnet="192.168.128.252/30",
            device_table=device_table)
        devices_with_no_ip = device_table.get_df().query("ip == ''")['mac'].tolist()
        self.assertEqual(1, len(devices_with_no_ip), "Expected there to be one device needing an IP")
        self.assertRaises(NetworkIsOutOfSpace, network_mapper.map_to_network_space)

    def test_duplicate_ips_in_device_table(self) :
        """Test NetworkMapper.map_to_network_space() where the device table contains duplicate IPs."""
        device_table_loader = DeviceTableLoader(
            known_devices_port=KnownDevicesTestAdapterForDuplicateIpTest(),
            active_clients_port=ActiveClientsTestAdapterForDuplicateIpTest(),
            fixed_ip_reservations_port=FixedIpReservationsTestAdapterForDuplicateIpTest()
        )
        device_table = device_table_loader.load_all()
        network_mapper = NetworkMapper(
            vlan_subnet="192.168.128.0/24",
            device_table=device_table)
        self.assertRaises(ValueError, network_mapper.map_to_network_space)