"""This is the main module for Netorg."""
import argparse
import logging
import sys
from adapters import activeclients_meraki
from adapters import configuration_jsonfile
from adapters import configurationwizard_console
from adapters import configurationwizard_sna_console
from adapters import devicetableout_console
from adapters import fixedipreservations_meraki
from adapters import knowndevices_yamlfile
from adapters import sna_hostgroups
from adapters import sna_session
from netorg_core import app

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

def create_net_organizer_app(debug_flag: bool) -> app.NetOrganizerApp:
    init_logging(debug_flag)
    configuration_port = configuration_jsonfile.NetorgConfigurationAdapter()
    config = configuration_port.load()
    net_organizer_app = app.NetOrganizerApp(
        known_devices_port=knowndevices_yamlfile.KnownDevicesAdapter(config),
        active_clients_port=activeclients_meraki.ActiveClientsAdapter(config),
        fixed_ip_reservations_port=fixedipreservations_meraki.FixedIpReservationsAdapter(config),
        device_table_csv_out_port=devicetableout_console.DeviceTableCsvOutAdapter(config),
        sna_hostgroup_port=sna_hostgroups.SecureNetworkAnalyticsHostGroupManagementAdapter(
            config,
            sna_session_port=sna_session.SecureNetworkAnalyticsSessionAdapter()
        )
    )
    return net_organizer_app

def do_configure() -> None:
    """Perform configure."""
    config_wizard = configurationwizard_console.ConfigurationWizardAdapter()
    config = config_wizard.generate()
    config_wizard_for_sna = configurationwizard_sna_console.ConfigurationWizardForSnaAdapter(
        sna_session_port=sna_session.SecureNetworkAnalyticsSessionAdapter())
    config_sna = config_wizard_for_sna.generate()
    merged = {**config,**config_sna}
    net_organizer_configurator = configuration_jsonfile.NetorgConfigurationAdapter()
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
