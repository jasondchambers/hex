from typing import List
from devicetable import DeviceTable
from networkspace import NetworkMapper
from ports import KnownDevice, KnownDevicesPort
from ports import ActiveClient, ActiveClientsPort
from ports import FixedIpReservation, FixedIpReservationsPort

class KnownDevicesMockAdapter(KnownDevicesPort):
    """Used for testing."""

    def __init__(self, seed_list: List[KnownDevice]) -> None:
        self.__list_of_known_devices = seed_list

    # overriding abstract method
    def load(self) -> List[KnownDevice]:
        return self.__list_of_known_devices

    # overriding abstract method
    def save(self,device_table: DeviceTable) -> None:
        self.__list_of_known_devices = self.__generate_list_of_known_devices(device_table)

    def __generate_list_of_known_devices(self, device_table: DeviceTable) -> List[KnownDevice]:
        list_of_known_devices: List[KnownDevice] = []
        df = device_table.df
        skip_these_macs = df.query("not known and reserved and not active").mac.unique().tolist()
        for index, row in df.iterrows():
            if row["mac"] not in skip_these_macs: 
                name = row['name'] 
                mac = row['mac'] 
                group = row['group'] 
                if group == "" : 
                    group = "unclassified"
                list_of_known_devices.append(KnownDevice(name=name, mac=mac, group=group))
        return list_of_known_devices
    
class ActiveClientsMockAdapter(ActiveClientsPort):

    def __init__(self, seed_list: List[ActiveClient]) -> None:
        self.__list_of_active_clients = seed_list

    # overriding abstract method
    def load(self) -> List[ActiveClient]:
        return self.__list_of_active_clients

class FixedIpReservationsMockAdapter(FixedIpReservationsPort):

    def __init__(self, vlan_subnet: str, seed_list: List[FixedIpReservation]) -> None:
        self.__vlan_subnet = vlan_subnet
        self.__list_of_fixed_ip_reservations = seed_list
        
    # overriding abstract method
    def load(self) -> List[FixedIpReservation]:
        return self.__list_of_fixed_ip_reservations

    # overriding abstract method
    def save(self,device_table: DeviceTable) -> None: #TODO
        network_mapper = NetworkMapper(self.__vlan_subnet,device_table)
        network_mapper.map_to_network_space()
        new_fixed_ip_reservations = self.__generate_list_of_fixed_ip_reservation(device_table)
        self.__list_of_fixed_ip_reservations = new_fixed_ip_reservations

    def __generate_list_of_fixed_ip_reservation(self, device_table: DeviceTable) -> List[FixedIpReservation]:
        list_of_fixed_ip_reservations: List[FixedIpReservation] = []
        df = device_table.df
        print(df)
        skip_these_macs = df.query("not known and reserved and not active").mac.unique().tolist()
        macs = df.mac.unique().tolist()
        for mac in macs :
            if mac not in skip_these_macs:
                device_df = df.query('mac == @mac')
                if device_df.shape[0] == 1:
                    ip = device_df.iloc[0]['ip']
                    name = device_df.iloc[0]['name']
                    fixed_ip_resevation = FixedIpReservation(mac=mac, name=name, ip_address=ip)
                    list_of_fixed_ip_reservations.append(fixed_ip_resevation)
        return list_of_fixed_ip_reservations