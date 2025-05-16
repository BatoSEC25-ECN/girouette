# pylint: disable = missing-module-docstring, missing-function-docstring

import logging
from logger import CustomFormatter

import keysight as ks
from plotter import comparison_analysis

from dataclass import (
    KeysightConfig,
    Channel,
    TimeBase,
    Trigger,
    TriggerSrc,
    SlopeType,
    VoltBase,
    FreqBase,
    ProbeRatio,
)

# Create the logger
# call:
# "logger = logging.getLogger(__name__)"
# at the top of your dependency to use the same shared logger instance (shared format)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.INFO, handlers={handler})

DEVICE_ADDR = "USB0::0x2A8D::0x0396::CN62117346::0::INSTR"

# Create channels
channel2 = Channel(
    number=1,
    name="MAX2231",
    vert_range=5,
    vert_range_unit=VoltBase.V,
    probe_ratio=ProbeRatio.RATIO_1,
)

channel3 = Channel(
    number=2,
    name="RECEIVER",
    vert_range=30,
    vert_range_unit=VoltBase.mV,
    probe_ratio=ProbeRatio.RATIO_1,
)

channel4 = Channel(
    number=3,
    name="PWM_XIAO",
    vert_range=2,
    vert_range_unit=VoltBase.V,
    probe_ratio=ProbeRatio.RATIO_1,
)


# Create trigger
trigger = Trigger(
    src=TriggerSrc.CHANNEL_3,
    slope=SlopeType.POSITIVE,
    threshold=2,
    threshold_unit=VoltBase.V,
)

# Create Keysight configuration
keysight_config = KeysightConfig(
    channels=[channel2, channel3, channel4],
    trigger=trigger,
    frequency=1,
    frequency_unit=FreqBase.MHz,
    hor_range=2,
    hor_range_unit=TimeBase.ms,
)

def main():
    device = ks.KeysightDevice(keysight_config)
    device.connect(DEVICE_ADDR)
    device.setup()
    device.capture()
    device.save_measures(name="test_no_wind")
    input("Press Enter to continue...")
    device.capture()
    device.save_measures(name="test_wind")
    device.release()

    comparison_analysis(
        csv_1="measurements/test_wind.csv",
        csv_2="measurements/test_no_wind.csv",
        slot=1,
        axis=3,
    )

if __name__ == "__main__":
    main()
