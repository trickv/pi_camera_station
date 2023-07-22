#!/usr/bin/env -S python -u

import modem as modem_module

modem = modem_module.modem()
modem.init()
modem.lte_configure()
modem.lte_connect()
modem.sync_clock()
modem.lte_disconnect()
