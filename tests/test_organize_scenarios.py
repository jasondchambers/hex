import unittest
from typing import List
from app import NetOrganizerApp
from networkspace import NetworkIsOutOfSpace
from ports import ActiveClient, FixedIpReservation, KnownDevice
from tests.mockadapters import ActiveClientsMockAdapter, FixedIpReservationsMockAdapter, KnownDevicesMockAdapter

class TestOrganizeScenarios(unittest.TestCase) :
    """Test cases for the organize feature."""

    def test_new_device_joins_network(self) :
        """A new device joins the network. As a new device, it will be active, but 
        it won't have a fixed IP reservation and it will not be a known device. 
        In this scenario, a new iPad has just joined the network: """

        known_devices: List[KnownDevice]= [
            # No known devices
        ]
        active_clients: List[ActiveClient] = [
            ActiveClient(mac='aa', name='Jasons iPad', ip_address='192.168.128.20')
        ]
        fixed_ip_reservations: List[FixedIpReservation] = [
            # No Fixed IP reservations
        ]
        known_devices_port=KnownDevicesMockAdapter(seed_list=known_devices)
        active_clients_port=ActiveClientsMockAdapter(seed_list=active_clients)
        fixed_ip_reservations_port=FixedIpReservationsMockAdapter(vlan_subnet='192.168.128.0/24',seed_list=fixed_ip_reservations)
        net_organizer_app = NetOrganizerApp(
            known_devices_port,
            active_clients_port,
            fixed_ip_reservations_port,
            device_table_csv_out_port=None,
            sna_hostgroup_port=None,
        )
        net_organizer_app.do_organize()
        post_organize_fixed_ip_reservations = fixed_ip_reservations_port.load()
        self.assertEqual(len(post_organize_fixed_ip_reservations), 1, "Expected there to be one new fixed IP reservation")
        self.assertEqual(post_organize_fixed_ip_reservations[0].mac, 'aa')
        self.assertEqual(post_organize_fixed_ip_reservations[0].name, 'Jasons iPad')
        self.assertEqual(post_organize_fixed_ip_reservations[0].ip_address, '192.168.128.20')
        post_organize_known_devices = known_devices_port.load()
        self.assertEqual(len(post_organize_known_devices), 1, "Expected there to be one new known device")
        self.assertEqual(post_organize_known_devices[0].mac, 'aa')
        self.assertEqual(post_organize_known_devices[0].name, 'Jasons iPad')
        self.assertEqual(post_organize_known_devices[0].group, 'unclassified')

        # Ok, at this point everything should be organized. So, let's try
        # and organize again and we should see there is nothing to do
        # detected by compating the state of fixed_ip_reservations and known_devices
        # before and after the second organize - they should be the same
        known_devices_port=KnownDevicesMockAdapter(seed_list=post_organize_known_devices)
        active_clients_port=ActiveClientsMockAdapter(seed_list=active_clients)
        fixed_ip_reservations_port=FixedIpReservationsMockAdapter(vlan_subnet='192.168.128.0/24',seed_list=post_organize_fixed_ip_reservations)
        net_organizer_app = NetOrganizerApp(
            known_devices_port,
            active_clients_port,
            fixed_ip_reservations_port,
            device_table_csv_out_port=None,
            sna_hostgroup_port=None,
        )
        net_organizer_app.do_organize()
        post_second_organize_fixed_ip_reservations = fixed_ip_reservations_port.load()
        self.assertCountEqual(post_organize_fixed_ip_reservations, post_second_organize_fixed_ip_reservations)
        post_second_organize_known_devices = known_devices_port.load()
        self.assertCountEqual(post_organize_known_devices, post_second_organize_known_devices)

    def test_missing_fixed_ip_reservation(self):
        """A device is active on the network. It is a known device, but for whatever
        reason it is missing a fixed IP reservation."""

        known_devices: List[KnownDevice]= [
            KnownDevice(name='Jasons iPad', mac='aa', group="jasons_devices")
        ]
        active_clients: List[ActiveClient] = [
            ActiveClient(mac='aa', name='Jasons iPad', ip_address='192.168.128.20')
        ]
        fixed_ip_reservations: List[FixedIpReservation] = [
            # Missing fixed IP reservation
        ]
        known_devices_port=KnownDevicesMockAdapter(seed_list=known_devices)
        active_clients_port=ActiveClientsMockAdapter(seed_list=active_clients)
        fixed_ip_reservations_port=FixedIpReservationsMockAdapter(vlan_subnet='192.168.128.0/24',seed_list=fixed_ip_reservations)
        net_organizer_app = NetOrganizerApp(
            known_devices_port,
            active_clients_port,
            fixed_ip_reservations_port,
            device_table_csv_out_port=None,
            sna_hostgroup_port=None,
        )
        net_organizer_app.do_organize()
        post_organize_fixed_ip_reservations = fixed_ip_reservations_port.load()
        self.assertEqual(len(post_organize_fixed_ip_reservations), 1, "Expected there to be one new fixed IP reservation")
        self.assertEqual(post_organize_fixed_ip_reservations[0].mac, 'aa')
        self.assertEqual(post_organize_fixed_ip_reservations[0].name, 'Jasons iPad')
        self.assertEqual(post_organize_fixed_ip_reservations[0].ip_address, '192.168.128.20')

    def test_retired_devices(self):
        """A device is not active and it is not a known device. However, it has a lingering 
        fixed IP reservation that needs to be cleaned up."""

        known_devices: List[KnownDevice]= [
            # No known devices
        ]
        active_clients: List[ActiveClient] = [
            # No active devices
        ]
        fixed_ip_reservations: List[FixedIpReservation] = [
            FixedIpReservation(mac='aa', name='Some Retired device', ip_address='192.168.128.20')
        ]
        known_devices_port=KnownDevicesMockAdapter(seed_list=known_devices)
        active_clients_port=ActiveClientsMockAdapter(seed_list=active_clients)
        fixed_ip_reservations_port=FixedIpReservationsMockAdapter(vlan_subnet='192.168.128.0/24',seed_list=fixed_ip_reservations)
        net_organizer_app = NetOrganizerApp(
            known_devices_port,
            active_clients_port,
            fixed_ip_reservations_port,
            device_table_csv_out_port=None,
            sna_hostgroup_port=None,
        )
        net_organizer_app.do_organize()
        post_organize_fixed_ip_reservations = fixed_ip_reservations_port.load()
        self.assertEqual(len(post_organize_fixed_ip_reservations), 0, "Expected there to be zero fixed IP reservations")

    def test_new_device_yet_to_join_network(self):
        """A new device that has been registered and is known. However, it is not active on
        the network and does not yet have an IP address."""

        known_devices: List[KnownDevice]= [
            KnownDevice(name='Jasons iPad', mac='aa', group="jasons_devices")
        ]
        active_clients: List[ActiveClient] = [
            # No active devices
        ]
        fixed_ip_reservations: List[FixedIpReservation] = [
            # Missing fixed IP reservation
        ]
        known_devices_port=KnownDevicesMockAdapter(seed_list=known_devices)
        active_clients_port=ActiveClientsMockAdapter(seed_list=active_clients)
        fixed_ip_reservations_port=FixedIpReservationsMockAdapter(vlan_subnet='192.168.128.0/24',seed_list=fixed_ip_reservations)
        net_organizer_app = NetOrganizerApp(
            known_devices_port,
            active_clients_port,
            fixed_ip_reservations_port,
            device_table_csv_out_port=None,
            sna_hostgroup_port=None,
        )
        net_organizer_app.do_organize()
        post_organize_fixed_ip_reservations = fixed_ip_reservations_port.load()
        self.assertEqual(len(post_organize_fixed_ip_reservations), 1, "Expected there to be one new fixed IP reservation")
        self.assertEqual(post_organize_fixed_ip_reservations[0].mac, 'aa')
        self.assertEqual(post_organize_fixed_ip_reservations[0].name, 'Jasons iPad')

    def test_activeip_different_to_fixedip(self):
        known_devices: List[KnownDevice]= [
            KnownDevice(name='Jasons Devices work laptop-JASCHAMB-M-XRDP', mac='f8:4d:89:7d:71:90', group="jasons_devices")
        ]
        active_clients: List[ActiveClient] = [
            ActiveClient(mac='f8:4d:89:7d:71:90', name='Jasons Devices work laptop-JASCHAMB-M-XRDP', ip_address='169.254.162.207')
        ]
        fixed_ip_reservations: List[FixedIpReservation] = [
            FixedIpReservation(mac='f8:4d:89:7d:71:90', name='Jasons Devices work laptop-JASCHAMB-M-XRDP', ip_address='192.168.128.237')
        ] 
        known_devices_port=KnownDevicesMockAdapter(seed_list=known_devices)
        active_clients_port=ActiveClientsMockAdapter(seed_list=active_clients)
        fixed_ip_reservations_port=FixedIpReservationsMockAdapter(vlan_subnet='192.168.128.0/24',seed_list=fixed_ip_reservations)
        net_organizer_app = NetOrganizerApp(
            known_devices_port,
            active_clients_port,
            fixed_ip_reservations_port,
            device_table_csv_out_port=None,
            sna_hostgroup_port=None,
        )
        net_organizer_app.do_organize()
        post_organize_fixed_ip_reservations = fixed_ip_reservations_port.load()
        self.assertEqual(len(post_organize_fixed_ip_reservations), 1, "Expected there to be one new fixed IP reservation")
        self.assertEqual(post_organize_fixed_ip_reservations[0].mac, 'f8:4d:89:7d:71:90')
        self.assertEqual(post_organize_fixed_ip_reservations[0].name, 'Jasons Devices work laptop-JASCHAMB-M-XRDP')
        self.assertEqual(post_organize_fixed_ip_reservations[0].ip_address, '192.168.128.237')

    def test_networkspace_exhausted(self):
        known_devices: List[KnownDevice]= [
            KnownDevice(name='Not enough space left for this device', mac='new', group="jasons_devices")
        ]
        active_clients: List[ActiveClient] = [
            ActiveClient(mac='active', name='active', ip_address='192.168.128.254')
        ]
        fixed_ip_reservations: List[FixedIpReservation] = [
            FixedIpReservation(mac='reserved', ip_address='192.168.128.253', name='reserved')
        ]
        known_devices_port=KnownDevicesMockAdapter(seed_list=known_devices)
        active_clients_port=ActiveClientsMockAdapter(seed_list=active_clients)
        fixed_ip_reservations_port=FixedIpReservationsMockAdapter(vlan_subnet='192.168.128.252/30',seed_list=fixed_ip_reservations)
        net_organizer_app = NetOrganizerApp(
            known_devices_port,
            active_clients_port,
            fixed_ip_reservations_port,
            device_table_csv_out_port=None,
            sna_hostgroup_port=None,
        )
        self.assertRaises(NetworkIsOutOfSpace, net_organizer_app.do_organize)