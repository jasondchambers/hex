"""Responsible for loading/saving groupings of known devices."""
import logging
from typing import List
import os.path
import yaml
from deepdiff import DeepDiff
from netorg_core import ports
from netorg_core import devicetable

class KnownDevicesAdapter(ports.KnownDevicesPort):
    """Responsible for loading/saving groupings of known devices."""
    # pylint: disable=logging-fstring-interpolation
    # pylint: disable=line-too-long

    def __init__(self, config: dict) -> None:
        self.__logger = logging.getLogger("netorg")
        self.filename = config['devices_yml']

    # overriding abstract method
    def load(self) -> List[ports.KnownDevice]:
        list_of_known_devices: List[ports.KnownDevice] = []
        if os.path.exists(self.filename) :
            self.__logger.debug(f"KnownDevicesAdapter.load() loading known devices from {self.filename}")
            with open(self.filename, encoding='utf8') as known_devices_file:
                yaml_data = yaml.load(known_devices_file, Loader=yaml.FullLoader)
                return self.__generate_list_of_known_devices(yaml_data)
        else:
            self.__logger.debug(f"KnownDevicesAdapter.load() {self.filename} not found")
        self.__logger.debug(f"KnownDevicesAdapter.load() returned {len(list_of_known_devices)} known devices")
        return list_of_known_devices

    # overriding abstract method
    def save(self,device_table: devicetable.DeviceTable) -> None:
        self.__logger.debug(f"KnownDevicesAdapter.save() saving known devices to {self.filename}")
        before = self.load()
        with open(self.filename, 'w', encoding='utf8') as devices_yml_file:
            devices_yml_file.write(self.__generate_yaml(device_table))
        after = self.load()
        self.__show_diffs(before, after)

    def __generate_yaml(self, device_table) -> str :
        """From the device table, generate the known devices file (devices.yml)."""
        # pylint: disable=invalid-name
        yaml_lines = []
        yaml_lines.append("devices:")
        df = device_table.get_df()
        skip_these_macs = df.query("not known and reserved and not active").mac.unique().tolist()
        groups = self.__get_groups(df)
        for group_name in groups :
            if group_name == "" :
                # Classify unknown devices as unclassified
                yaml_lines.append("  unclassified:")
            else :
                yaml_lines.append(f'  {group_name}:')
            devices_in_group = self.__get_devices_in_group(df,group_name,skip_these_macs)
            for device_in_group in devices_in_group :
                yaml_lines.append(f'    - {device_in_group}')
        entire_yaml = '\n'.join(yaml_lines)
        return entire_yaml

    # pylint: disable=invalid-name
    def __get_devices_in_group(self, df, group, skip_these_macs) -> list :
        """Produce a list of all devices in a group."""
        devices = []
        # pylint: disable=unused-variable
        for index, row in df.query(f'group == "{group}"').iterrows():
            if row["mac"] not in skip_these_macs:
                devices.append(f'{row["name"]},{row["mac"]}')
            else:
                self.__logger.debug(f'Skipping {row["name"]},{row["mac"]}')
        return devices

    def __get_groups(self, df) -> list :
        """Produce a list of all unique groups in the device table."""
        return df.group.unique().tolist()

    def __show_diffs(self,old_list, new_list):
        """Show the before and after of the known devices to highlight new devices."""
        diff = DeepDiff(old_list, new_list)
        if diff:
            self.__logger.info("Known devices (devices.yml) differences are as follows:")
            if 'iterable_item_added' in diff:
                self.__logger.info("  Adding devices:")
                added_dict = diff['iterable_item_added']
                # pylint: disable=unused-variable
                for key,val in added_dict.items():
                    self.__logger.info(f'    {val.group}: {val.name} {val.mac}')
            else:
                self.__logger.info("  There are no new devices")
        else:
            self.__logger.info("There are no changes to known devices (devices.yml)")

    def __generate_list_of_known_devices(self, yaml_data) -> List[ports.KnownDevice]:
        """Generate list of known devices from YAML data."""
        if not isinstance(yaml_data, dict):
            raise ValueError("Invalid YAML")
        if 'devices' not in yaml_data:
            raise ValueError("Invalid YAML")
        list_of_known_devices: List[ports.KnownDevice] = []
        devices = yaml_data['devices']
        device_group_names = devices.keys()
        for device_group_name in device_group_names:
            devices_in_group = devices[device_group_name]
            for device_in_group in devices_in_group:
                device_in_group_str = device_in_group.split(',')
                device_name = device_in_group_str[0]
                device_mac = device_in_group_str[1]
                known_device = ports.KnownDevice(
                    name=device_name,
                    mac=device_mac,
                    group=device_group_name)
                list_of_known_devices.append(known_device)
        return list_of_known_devices
