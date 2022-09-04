from typing import List
from netorg_core import devicetable
from netorg_core import networkspace
from netorg_core import ports

class KnownDevicesAdapter(ports.KnownDevicesPort):
    """Used for testing."""

    def __init__(self, seed_list: List[ports.KnownDevice]) -> None:
        self.__list_of_known_devices = seed_list

    # overriding abstract method
    def load(self) -> List[ports.KnownDevice]:
        return self.__list_of_known_devices

    # overriding abstract method
    def save(self,device_table: devicetable.DeviceTable) -> None:
        self.__list_of_known_devices = self.__generate_list_of_known_devices(device_table)

    def __generate_list_of_known_devices(self, device_table: devicetable.DeviceTable) -> List[ports.KnownDevice]:
        list_of_known_devices: List[ports.KnownDevice] = []
        df = device_table.get_df()
        skip_these_macs = df.query("not known and reserved and not active").mac.unique().tolist()
        for index, row in df.iterrows():
            if row["mac"] not in skip_these_macs: 
                name = row['name'] 
                mac = row['mac'] 
                group = row['group'] 
                if group == "" : 
                    group = "unclassified"
                list_of_known_devices.append(ports.KnownDevice(name=name, mac=mac, group=group))
        return list_of_known_devices
    
class ActiveClientsAdapter(ports.ActiveClientsPort):

    def __init__(self, seed_list: List[ports.ActiveClient]) -> None:
        self.__list_of_active_clients = seed_list

    # overriding abstract method
    def load(self) -> List[ports.ActiveClient]:
        return self.__list_of_active_clients

class FixedIpReservationsAdapter(ports.FixedIpReservationsPort):

    def __init__(self, vlan_subnet: str, seed_list: List[ports.FixedIpReservation]) -> None:
        self.__vlan_subnet = vlan_subnet
        self.__list_of_fixed_ip_reservations = seed_list
        
    # overriding abstract method
    def load(self) -> List[ports.FixedIpReservation]:
        return self.__list_of_fixed_ip_reservations

    # overriding abstract method
    def save(self,device_table: devicetable.DeviceTable) -> None: #TODO
        network_mapper = networkspace.NetworkMapper(self.__vlan_subnet,device_table)
        network_mapper.map_to_network_space()
        new_fixed_ip_reservations = self.__generate_list_of_fixed_ip_reservation(device_table)
        self.__list_of_fixed_ip_reservations = new_fixed_ip_reservations

    def __generate_list_of_fixed_ip_reservation(self, device_table: devicetable.DeviceTable) -> List[ports.FixedIpReservation]:
        list_of_fixed_ip_reservations: List[ports.FixedIpReservation] = []
        df = device_table.get_df()
        skip_these_macs = df.query("not known and reserved and not active").mac.unique().tolist()
        macs = df.mac.unique().tolist()
        for mac in macs :
            if mac not in skip_these_macs:
                device_df = df.query('mac == @mac')
                if device_df.shape[0] == 1:
                    ip = device_df.iloc[0]['ip']
                    name = device_df.iloc[0]['name']
                    fixed_ip_resevation = ports.FixedIpReservation(mac=mac, name=name, ip_address=ip)
                    list_of_fixed_ip_reservations.append(fixed_ip_resevation)
        return list_of_fixed_ip_reservations