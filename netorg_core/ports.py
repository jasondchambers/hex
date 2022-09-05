from typing import NamedTuple
from abc import ABC, abstractmethod
from typing import List
import requests

from netorg_core import devicetable

class KnownDevice(NamedTuple):
    name: str
    mac: str
    group: str

    def __str__(self) -> str:
        return f'Known device: {self.name} with MAC {self.mac} in {self.group}'

class ActiveClient(NamedTuple):
    mac: str
    name: str
    #description: str
    ip_address: str

    def __str__(self) -> str:
        #return f'Active client: {self.name} {self.description} with MAC {self.mac} has IP address {self.ip_address}'
        return f'Active client: {self.name} with MAC {self.mac} has IP address {self.ip_address}'

class FixedIpReservation(NamedTuple):
    mac: str
    name: str
    ip_address: str

    def __str__(self) -> str:
        return f'Fixed IP reservation: {self.mac} {self.name} {self.ip_address}'

class KnownDevicesPort(ABC):

    @abstractmethod
    def load(self) -> List[KnownDevice]:
        pass

    @abstractmethod
    def save(self,device_table: devicetable.DeviceTable) -> None:
        pass

class ActiveClientsPort(ABC):

    @abstractmethod
    def load(self) -> List[ActiveClient]:
        pass

class FixedIpReservationsPort(ABC):

    @abstractmethod
    def load(self) -> List[FixedIpReservation]:
        pass

    @abstractmethod
    def save(self,device_table: devicetable.DeviceTable) -> None:
        pass

class NetorgConfigurationPort(ABC):

    @abstractmethod
    def load(self) -> dict:
        pass

    @abstractmethod
    def save(self,config: dict):
        pass

class ConfigurationWizardPort(ABC):

    @abstractmethod
    def generate(self) -> dict:
        pass

class DeviceTableCsvOutPort(ABC):

    @abstractmethod
    def write(self,device_table_csv: str):
        pass

class SecureNetworkAnalyticsHostGroupManagementPort(ABC): #TODO

    @abstractmethod
    def update_host_groups(self,device_table: devicetable.DeviceTable) -> None: #TODO
        pass

    class FailedToCreateHostGroup(Exception) :
        pass

    class FailedToUpdateHostGroup(Exception) :
        pass

    class FailedToDeleteHostGroup(Exception) :
        pass

class SecureNetworkAnalyticsSessionPort(ABC):

    @abstractmethod
    def login(host: str, user: str, password: str) -> None:
        pass

    @abstractmethod
    def logout() -> None:
        pass

    @abstractmethod
    def get_host() -> str:
        pass

    @abstractmethod
    def get_tenant_id() -> str:
        pass

    @abstractmethod
    def get_api_session() -> requests.Session:
        pass

    class FailedToLogin(Exception) :
        pass