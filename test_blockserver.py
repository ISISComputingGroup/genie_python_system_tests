import json
import unittest

from genie_python.utilities import compress_and_hex

from utilities import utilities
import time
from genie_python import genie as g


SECONDS_TO_WAIT_FOR_IOC_STARTS = 120


class TestBlockserver(unittest.TestCase):
    """
    Tests for top-level functionality of block server
    """
    def setUp(self) -> None:
        g.set_instrument(None, import_instrument_init=False)

    def test_GIVEN_config_changes_by_block_THEN_iocs_do_not_restart_except_for_caenv895(self):
        utilities.load_config_if_not_already_loaded("test_blockserver")

        utilities.wait_for_iocs_to_be_up(["SIMPLE", "CAENV895_01"], SECONDS_TO_WAIT_FOR_IOC_STARTS)

        time.sleep(60)  # Time for IOCs to fully boot etc

        simple_start_time_before = g.get_pv("CS:IOC:SIMPLE:DEVIOS:STARTTOD", is_local=True)
        caen_start_time_before = g.get_pv("CS:IOC:CAENV895_01:DEVIOS:STARTTOD", is_local=True)

        details = utilities.get_config_details()
        details["desc"] = "some_edited_description"
        g.set_pv("CS:BLOCKSERVER:SET_CURR_CONFIG_DETAILS", compress_and_hex(json.dumps(details)), is_local=True)

        err = None
        for _ in range(SECONDS_TO_WAIT_FOR_IOC_STARTS):
            try:
                self.assertEqual(simple_start_time_before, g.get_pv("CS:IOC:SIMPLE:DEVIOS:STARTTOD", is_local=True),
                                 "SIMPLE ioc should not have restarted")
                self.assertNotEqual(caen_start_time_before, g.get_pv("CS:IOC:CAENV895_01:DEVIOS:STARTTOD", is_local=True),
                                    "CAENV895 ioc should have restarted")
                break
            except (Exception, AssertionError) as e:
                err = e
                time.sleep(1)
        else:
            raise err
