from netorg_core import ports

class DeviceTableCsvOutAdapter(ports.DeviceTableCsvOutPort):

    def __init__(self, config: dict) -> None:
        pass

    # overriding abstract method
    def write(self,device_table_csv: str):
        print(device_table_csv)