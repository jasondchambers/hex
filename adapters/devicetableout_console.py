"""Provides a console based adapter for outputting the device table."""
from netorg_core import ports

class DeviceTableCsvOutAdapter(ports.DeviceTableCsvOutPort):
    """Provides a console based adapter for outputting the device table."""
    # pylint: disable=too-few-public-methods

    def __init__(self, config: dict) -> None:
        pass

    # overriding abstract method
    def write(self,device_table_csv: str):
        print(device_table_csv)
