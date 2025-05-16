# pylint: disable = missing-module-docstring, invalid-name

from dataclasses import dataclass
from typing import List
from enum import Enum


class TriggerSource(Enum):
    """Trigger name enumeration."""

    CHANNEL_1 = "CHANnel1"
    CHANNEL_2 = "CHANnel2"
    CHANNEL_3 = "CHANnel3"
    CHANNEL_4 = "CHANnel4"
    EXTERNAL = "EXTernal"


class VoltageUnit(Enum):
    """
    Range unit enumeration.
    Represents channel range in value/div (vertical scale).
    """

    V = 1
    mV = 1e-3


class FrequencyUnit(Enum):
    """
    Frequency unit enumeration.
    Represents channel frequency in Hz (horizontal scale).
    """

    HZ = 1
    KHz = 1e3
    MHz = 1e6


class ProbeRatio(Enum):
    """
    Probe scale enumeration.
    Represents probe ratio (either x1 or x10).
    """

    X1 = "1"
    X10 = "10"


class SlopeType(Enum):
    """Trigger slope enumeration."""

    POSITIVE = "POS"
    NEGATIVE = "NEG"
    ETIHER = "EITH"
    ALTERNATE = "ALT"


class TimeUnit(Enum):
    """
    Time unit enumeration.
    Represents time in seconds.
    """

    S = 1
    MS = 1e-3
    US = 1e-6


@dataclass
class Channel:
    """Represents a measurement channel."""

    number: int
    name: str

    vertical_range: int = 1
    vertical_unit: VoltageUnit = VoltageUnit.V

    offset: int = 0
    offset_unit: VoltageUnit = VoltageUnit.V

    probe_ratio: ProbeRatio = ProbeRatio.X1

    def __post_init__(self):
        self._validate_channel()

    def _validate_channel(self):
        if not (1 <= self.number <= 4):
            raise ValueError("Channel number must be between 1 and 4.")
        if not isinstance(self.name, str) or not self.name or len(self.name) >= 10:
            raise ValueError(
                "Name must be a non-empty string with fewer than 10 characters."
            )

        if not isinstance(self.vertical_range, int) or self.vertical_range <= 0:
            raise ValueError("Vertical range must be a positive integer.")
        if not isinstance(self.vertical_unit, VoltageUnit):
            raise ValueError("Invalid vertical unit.")
        if not isinstance(self.probe_ratio, ProbeRatio):
            raise ValueError("Invalid probe ratio.")
        if not isinstance(self.offset, int):
            raise ValueError("Offset must be an integer.")
        if not isinstance(self.offset_unit, VoltageUnit):
            raise ValueError("Invalid offset unit.")

        offset_volts = self.offset / self.offset_unit.value
        range_volts = self.vertical_range / self.vertical_unit.value
        if abs(offset_volts) > range_volts:
            raise ValueError("Offset must be within the vertical range ±range.")


@dataclass
class Trigger:
    """Represents a trigger configuration."""

    source: TriggerSource = TriggerSource.EXTERNAL
    slope: SlopeType = SlopeType.POSITIVE
    threshold: int = 1
    threshold_unit: VoltageUnit = VoltageUnit.V

    def __post_init__(self):
        self._validate_trigger()

    def _validate_trigger(self):
        if not isinstance(self.source, TriggerSource):
            raise ValueError("Invalid trigger source.")
        if not isinstance(self.slope, SlopeType):
            raise ValueError("Invalid slope type.")
        if not isinstance(self.threshold, (int, float)) or self.threshold <= 0:
            raise ValueError("Threshold must be a positive number.")
        if not isinstance(self.threshold_unit, VoltageUnit):
            raise ValueError("Invalid threshold unit.")


@dataclass
class KeysightConfig:
    """Top-level configuration for Keysight measurement system."""

    channels: List[Channel]
    trigger: Trigger

    horizontal_range: int = 100
    horizontal_unit: TimeUnit = TimeUnit.MS

    frequency: int = 1
    frequency_unit: FrequencyUnit = FrequencyUnit.HZ

    def __post_init__(self):
        self._validate_config()

    def _validate_config(self):
        if not isinstance(self.channels, list) or not self.channels:
            raise ValueError("Channels must be a non-empty list.")
        if not all(isinstance(ch, Channel) for ch in self.channels):
            raise ValueError("All items in channels must be Channel instances.")
        if not isinstance(self.trigger, Trigger):
            raise ValueError("Trigger must be a Trigger instance.")

        if not isinstance(self.frequency, int) or self.frequency <= 0:
            raise ValueError("Frequency must be a positive integer.")
        if not isinstance(self.frequency_unit, FrequencyUnit):
            raise ValueError("Invalid frequency unit.")
        if not isinstance(self.horizontal_range, int) or self.horizontal_range <= 0:
            raise ValueError("Horizontal range must be a positive integer.")
        if not isinstance(self.horizontal_unit, TimeUnit):
            raise ValueError("Invalid horizontal time unit.")
