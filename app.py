"""
The main NetOrganizerApp which supports all the top-level use cases.
Should be dependent only on ports - never directly adapaters.
"""
from devicetableloader import DeviceTableLoader
from ports import ActiveClientsPort, DeviceTableCsvOutPort, FixedIpReservationsPort
from ports import KnownDevicesPort, SecureNetworkAnalyticsHostGroupManagementPort
from scan import NetorgScanner

class NetOrganizerApp():
    """The main NetOrganizerApp which supports all the top-level use cases."""

    # pylint: disable=too-many-arguments
    def __init__(self,
                 known_devices_port: KnownDevicesPort,
                 active_clients_port: ActiveClientsPort,
                 fixed_ip_reservations_port: FixedIpReservationsPort,
                 device_table_csv_out_port: DeviceTableCsvOutPort,
                 sna_hostgroup_port: SecureNetworkAnalyticsHostGroupManagementPort) -> None:
        self.known_devices_port = known_devices_port
        self.active_clients_port = active_clients_port
        self.fixed_ip_reservations_port = fixed_ip_reservations_port
        self.device_table_csv_out_port = device_table_csv_out_port
        self.sna_hostgroup_port = sna_hostgroup_port

    def do_scan(self) -> None:
        """Perform a scan."""
        device_table = self.__load_device_table()
        self.known_devices_port.save(device_table)
        scanner = NetorgScanner(device_table)
        scanner.run()
        scanner.report()

    def do_organize(self) -> None:
        """Organize the network."""
        device_table = self.__load_device_table()
        self.known_devices_port.save(device_table)
        self.fixed_ip_reservations_port.save(device_table)
        if self.sna_hostgroup_port:
            self.sna_hostgroup_port.update_host_groups(device_table)

    def do_export(self) -> None:
        """Export the devices table."""
        device_table = self.__load_device_table()
        self.device_table_csv_out_port.write(device_table.df.to_csv())

    def __load_device_table(self):
        """Load the device table."""
        device_table_loader = DeviceTableLoader(
            self.known_devices_port,
            self.active_clients_port,
            self.fixed_ip_reservations_port)
        return device_table_loader.load_all()
