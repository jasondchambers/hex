"""This is the main module for Netorg."""
import argparse
import logging
import sys
from adapters.activeclients_meraki import ActiveClientsMerakiAdapter
from adapters.configuration_jsonfile import NetorgConfigurationJsonFileAdapter
from adapters.configurationwizard import ConfigurationWizardConsoleAdapter
from adapters.configurationwizard_sna import ConfigurationWizardForSnaConsoleAdapter
from adapters.devicetableout_console import DeviceTableCsvOutConsoleAdapter
from adapters.fixedipreservations_meraki import FixedIpReservationsMerakiAdapter
from adapters.knowndevices_yamlfile import KnownDevicesYamlFileAdapter
from adapters.sna_hostgroups import SecureNetworkAnalyticsHostGroupManagementAdapter
from adapters.sna_session import SecureNetworkAnalyticsSessionAdapter
from app import NetOrganizerApp

def init_logging(debug_flag: bool) -> None:
    """ Initialize logging so that 
           only debug, info -> stdout (and only stdout)
           only warning, error, critical -> stderr (and only stderr)
    """
    class InfoFilter(logging.Filter):
        def filter(self, rec):
            return rec.levelno in (logging.DEBUG, logging.INFO)

    logger = logging.getLogger("netorg")
    info_channel = logging.StreamHandler(sys.stdout)
    info_channel.addFilter(InfoFilter())
    if debug_flag:
        logger.setLevel(logging.DEBUG)
        info_channel.setLevel(logging.DEBUG)
        info_channel.setFormatter(
            logging.Formatter(
                fmt='%(asctime)s %(name)12s: %(levelname)8s > %(message)s', 
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
    else:
        logger.setLevel(logging.INFO)
        info_channel.setLevel(logging.INFO)
        info_channel.setFormatter(
            logging.Formatter(
                fmt='%(message)s'
            )
        )
    error_channel = logging.StreamHandler()
    error_channel.setLevel(logging.WARNING)
    logger.addHandler(info_channel)
    logger.addHandler(error_channel)

def create_net_organizer_app(debug_flag: bool) -> NetOrganizerApp:
    init_logging(debug_flag)
    configuration_port = NetorgConfigurationJsonFileAdapter()
    config = configuration_port.load()
    net_organizer_app = NetOrganizerApp(
        known_devices_port=KnownDevicesYamlFileAdapter(config),
        active_clients_port=ActiveClientsMerakiAdapter(config),
        fixed_ip_reservations_port=FixedIpReservationsMerakiAdapter(config),
        device_table_csv_out_port=DeviceTableCsvOutConsoleAdapter(config),
        sna_hostgroup_port=SecureNetworkAnalyticsHostGroupManagementAdapter(
            config,
            sna_session_port=SecureNetworkAnalyticsSessionAdapter()
        )
    )
    return net_organizer_app

def do_configure() -> None:
    """Perform configure."""
    config_wizard = ConfigurationWizardConsoleAdapter()
    config = config_wizard.generate()
    config_wizard_for_sna = ConfigurationWizardForSnaConsoleAdapter(
        sna_session_port=SecureNetworkAnalyticsSessionAdapter())
    config_sna = config_wizard_for_sna.generate()
    merged = {**config,**config_sna}
    net_organizer_configurator = NetorgConfigurationJsonFileAdapter()
    net_organizer_configurator.save(merged)

def get_parser() -> argparse.ArgumentParser:
    """Figure out what the user wants to happen and make it so."""
    parser = argparse.ArgumentParser(description='Organize your network.')
    parser.add_argument("-v", "--verbose", 
                        help="Useful for debugging", 
                        action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--configure", 
                       help="[Re-]Configure Netorg.",
                       action="store_true")
    group.add_argument("-s", "--scan", 
                       help="Scan to discover new devices, query active devices and fixed IP reservations. Generate/update known devices (devices.yml).",
                       action="store_true")
    group.add_argument("-o", "--organize", 
                       help="Organize the network. If configured, push changes to Secure Network Analytics.",
                       action="store_true")
    group.add_argument("-e", "--export", 
                       help="Export the device table",
                       action="store_true")
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    debug_flag = False
    if args.verbose:
        debug_flag = True
    if args.configure:
        do_configure()
    elif args.scan:
        net_organizer_app = create_net_organizer_app(debug_flag)
        net_organizer_app.do_scan()
    elif args.organize:
        net_organizer_app = create_net_organizer_app(debug_flag)
        net_organizer_app.do_organize()
    elif args.export:
        net_organizer_app = create_net_organizer_app(debug_flag)
        net_organizer_app.do_export()
    else:
        parser.print_help(sys.stderr)

if __name__ == "__main__":
    main()
