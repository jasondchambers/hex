"""
Contains all of the ports. See the Ports and Adapters (aka Hexagonal Architecture) for details.
https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)
"""
from typing import NamedTuple
from typing import List
from abc import ABC, abstractmethod
import requests
from netorg_core import devicetable

# pylint: disable=too-few-public-methods
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

class KnownDevice(NamedTuple):
    """A device that is known and has been assigned to some group."""
    name: str
    mac: str
    group: str

    def __str__(self) -> str:
        return f'Known device: {self.name} with MAC {self.mac} in {self.group}'

class ActiveClient(NamedTuple):
    """A device that has a current DHCP lease."""
    mac: str
    name: str
    ip_address: str

    def __str__(self) -> str:
        return f'Active client: {self.name} with MAC {self.mac} has IP address {self.ip_address}'

class FixedIpReservation(NamedTuple):
    """A device that has a reserved/fixed IP address with the DHCP server."""
    mac: str
    name: str
    ip_address: str

    def __str__(self) -> str:
        return f'Fixed IP reservation: {self.mac} {self.name} {self.ip_address}'

class KnownDevicesPort(ABC):
    """Port for loading/saving known devices."""

    @abstractmethod
    def load(self) -> List[KnownDevice]:
        pass

    @abstractmethod
    def save(self,device_table: devicetable.DeviceTable) -> None:
        pass

class ActiveClientsPort(ABC):
    """Port for loading active devices."""

    @abstractmethod
    def load(self) -> List[ActiveClient]:
        pass

class FixedIpReservationsPort(ABC):
    """Port for loading/saving fixed IP reservations."""

    @abstractmethod
    def load(self) -> List[FixedIpReservation]:
        pass

    @abstractmethod
    def save(self,device_table: devicetable.DeviceTable) -> None:
        pass

class NetorgConfigurationPort(ABC):
    """Port for loading/saving Netorg configuration."""

    @abstractmethod
    def load(self) -> dict:
        pass

    @abstractmethod
    def save(self,config: dict):
        pass

class ConfigurationWizardPort(ABC):
    """Port for a configuration wizard which generates a config."""

    @abstractmethod
    def generate(self) -> dict:
        pass

class DeviceTableCsvOutPort(ABC):
    """Output port for writing a CSV of the device table."""

    @abstractmethod
    def write(self,device_table_csv: str):
        pass

class SecureNetworkAnalyticsHostGroupManagementPort(ABC):
    """Output port for updating host groups in Secure Network Analytics."""

    @abstractmethod
    def update_host_groups(self,device_table: devicetable.DeviceTable) -> None:
        pass

    class FailedToCreateHostGroup(Exception) :
        pass

    class FailedToUpdateHostGroup(Exception) :
        pass

    class FailedToDeleteHostGroup(Exception) :
        pass

class SecureNetworkAnalyticsSessionPort(ABC):
    """Port for managing Secure Network Analytics session."""

    @abstractmethod
    def login(self, host: str, user: str, password: str) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    @abstractmethod
    def get_host(self) -> str:
        pass

    @abstractmethod
    def get_tenant_id(self) -> str:
        pass

    @abstractmethod
    def get_api_session(self) -> requests.Session:
        pass

    class FailedToLogin(Exception) :
        pass
