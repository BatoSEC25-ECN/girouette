# pylint: disable = missing-module-docstring, missing-function-docstring, missing-class-docstring
# pylint: disable = broad-exception-caught, unspecified-encoding
# pylint: disable = logging-fstring-interpolation

import logging
import os
import sys
import time
from decimal import Decimal

import csv
import pyvisa

MAX_CHAN: int = 4

from dataclass import (
    KeysightConfig,
    Channel,
    TimeBase,
)

DEVICE_TIMEOUT: int = 60000  # 60 seconds timeout
TRIG_THRESHOLD: float = 1.5  # Trigger threshold in volts
DEFAULT_OUTPUT_DIR: str = "measurements"  # Default output directory
DEFAULT_MEAS_NAME: str = "measure"  # Default measurement name

# Set up logging
logger = logging.getLogger(__name__)


class KeysightDevice:
    def __init__(self, conf: KeysightConfig):
        self.conf = conf
        self.device: str = None
        self.waveforms = {}

    @staticmethod
    def float_to_nr3(nb: float) -> str:
        return f"{Decimal(nb):.1E}"

    def time_to_nr3(self, value: int, time_base: TimeBase) -> str:
        return self.float_to_nr3(value * time_base.value / 10)

    def _device_write(self, cmd: str):
        try:
            self.device.write(cmd)
            logger.debug('Command "%s" sent.', cmd)
        except Exception as e:
            logger.error("Writing to device failed, %s", e)

    def _device_read(self, cmd: str) -> str:
        try:
            ret = self.device.query(cmd)
            logger.debug('Read command "%s" sent.\n Answer is %s', cmd, ret)
            return ret
        except Exception as e:
            logger.error("Reading from device failed, %s", e)

    def _hw_reset(self):
        self._device_write("*RST")
        self._device_write("*CLS")
        self._device_write(":STOP")

        for ch in range(1, MAX_CHAN + 1):
            self._device_write(f":CHANnel{ch}:DISPlay OFF")

        logger.debug("Reset done.")

    def _hw_setup_time_base(self):
        self._device_write(
            f":TIMebase:SCALe {self.time_to_nr3(self.conf.hor_range, self.conf.hor_range_unit)}"
        )
        self._device_write(":TIMebase:REFerence LEFT")
        self._device_write(":TIMebase:POSition 0")
        logger.debug("Time base setup done.")

    def _hw_setup_acquisition(self):
        self._device_write(":ACQuire:TYPE NORMal")
        logger.debug("Acquisition setup done.")

    def _hw_setup_ext_channel(self):
        self._device_write(":EXTernal:POSition 0")
        self._device_write(":EXTernal:PROBe 1")
        trig = self.conf.trigger
        self._device_write(
            f":EXTernal:RANGe {trig.threshold}{trig.threshold_unit.value}"
        )
        logger.debug("External channel setup done.")

    def _hw_setup_channels(self):
        for ch in self.conf.channels:
            no: int = ch.number
            self._device_write(f":CHANnel{no}:DISPlay ON")
            self._device_write(f":CHANnel{no}:COUPling DC")
            self._device_write(f":CHANnel{no}:UNITs VOLT")
            self._device_write(f":CHANnel{no}:LABel {ch.name}")
            self._device_write(f":CHANnel{no}:DISPlay:LABel ON")
            self._device_write(f":CHANnel{no}:PROBe {ch.probe_ratio.value}")
            self._device_write(
                f":CHANnel{no}:SCALe {ch.vert_range} {ch.vert_range_unit.name}"
            )
            self._device_write(
                f":CHANnel{no}:OFFSet {ch.offset} {ch.offset_unit.value}"
            )
            logger.debug(f"Channel{no} setup done.")

    def _hw_setup_trigger(self):
        trig = self.conf.trigger

        self._device_write(":TRIGger:MODE EDGE")
        self._device_write(f":TRIGger:EDGE:SOURce {trig.src.value}")
        self._device_write(f":TRIGger:EDGE:SLOPe {trig.slope.value}")
        self._device_write(f":TRIGger:EDGE:LEVel {self.float_to_nr3(trig.threshold)}")
        logger.debug("Trigger setup done.")

    def _hw_acquire(self):
        try:
            self._device_write(":WAVeform:FORMat ASCII")
            self._device_write(":WAVeform:POINts:MODE NORMal")

            # Calculate the number of points based on the horizontal scale and required frequency
            time_range = 10 * self.conf.hor_range * self.conf.hor_range_unit.value
            freq = self.conf.frequency * self.conf.frequency_unit.value
            num_points = int(time_range * freq)
            self._device_write(f":WAVeform:POINts {num_points}")

            logger.info("Waiting for trigger")

            self._device_read("*OPC?")
            self._device_write(":SINGLE")

            ret = self._device_read(":OPERegister:CONDition?")
            while (int(ret) & 0b1000) != 0:
                time.sleep(0.001)
                ret = self._device_read(":OPERegister:CONDition?")

            logger.info("Trigger detected")
        except Exception as e:
            logger.error("Reading from device failed, %s", e)

    def connect(self, address: str):
        logger.info("Connecting to target")
        try:
            rm = pyvisa.ResourceManager()
            try:
                self.device = rm.open_resource(address)
                self.device.timeout = DEVICE_TIMEOUT
            except Exception:
                devices = rm.list_resources()
                logger.error(
                    f"No device found.\nAvailable devices are: {','.join([d for d in devices])}"
                )
                sys.exit(-1)

            # Store configuration and initialize device
            self._hw_reset()

        except Exception as e:
            logger.error("%s", e)
            sys.exit(-1)

        logger.info('Connected to "%s"', address)

    def setup(self):
        try:
            logger.info("Running setup")
            self._hw_setup_acquisition()
            self._hw_setup_time_base()
            self._hw_setup_ext_channel()
            self._hw_setup_channels()
            self._hw_setup_trigger()
            logger.info("Device setup done")
        except KeyboardInterrupt:
            self.release()

    def capture(self):
        def extract_data(ch: Channel) -> list[Channel]:
            self._device_write(f":WAVeform:SOURce CHANnel{ch.number}")
            try:
                data = self._device_read(":WAVeform:DATA?").strip()
                values = data.split(",")
                logger.info(f"Channel{ch.name}: collected {len(values)} points")
                return values
            except Exception as e:
                logger.error(e)
                return []

        try:
            self._hw_acquire()
            waveforms = {}
            for ch in self.conf.channels:
                logger.info(
                    f'Extracting measure points from channel {ch.number}:"{ch.name}"'
                )
                data = extract_data(ch)
                waveforms[ch.name] = [float(v) for v in data[1 : len(data)]]
            self.waveforms = waveforms
            logger.info("Data retrieval done")
        except KeyboardInterrupt:
            self.release()

    def save_measures(
        self,
        folder: str = DEFAULT_OUTPUT_DIR,
        name: str = DEFAULT_MEAS_NAME,
    ) -> str:
        logger.info("Creating data file from collected measures")

        os.makedirs(folder, exist_ok=True)
        file = os.path.join(folder, f"{name.split(".", 1)[0]}.csv")

        waveforms = self.waveforms
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)

            header = ["Timestamp"] + [ch.name for ch in self.conf.channels]
            writer.writerow(header)

            col_data_min = min(len(a) for a in waveforms.values())

            for i in range(col_data_min - 1):
                sampling_duration = self.conf.hor_range * self.conf.hor_range_unit.value
                time_inc = sampling_duration / col_data_min
                time_stamp = i * time_inc
                row = [time_stamp] + [
                    waveforms[ch.name][i] for ch in self.conf.channels
                ]
                writer.writerow(row)
        logger.info("CSV file created: %s", file)
        return file

    def release(self):
        logger.info("Releasing device connection")
        self.device.close()
        logger.info("Device released")
