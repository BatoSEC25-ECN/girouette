# pylint: disable = missing-module-docstring, invalid-name

from dataclasses import dataclass
from typing import List
from enum import Enum


class TriggerSrc(Enum):
    """Trigger name enumeration."""

    CHANNEL_1 = "CHANnel1"
    CHANNEL_2 = "CHANnel2"
    CHANNEL_3 = "CHANnel3"
    CHANNEL_4 = "CHANnel4"
    EXTERNAL = "EXTernal"


class VoltBase(Enum):
    """
    Range unit enumeration.
    Represents channel range in value/div (vertical scale).
    """

    V = 1
    mV = 1e-3


class FreqBase(Enum):
    """
    Frequency unit enumeration.
    Represents channel frequency in Hz (horizontal scale).
    """

    H = 1
    KHz = 1e3
    MHz = 1e6


class ProbeRatio(Enum):
    """
    Probe scale enumeration.
    Represents probe ratio (either x1 or x10).
    """

    RATIO_1 = "1"
    RATIO_10 = "10"


class SlopeType(Enum):
    """Trigger slope enumeration."""

    POSITIVE = "POS"
    NEGATIVE = "NEG"
    ETIHER = "EITH"
    ALTERNATE = "ALT"


class TimeBase(Enum):
    """
    Time unit enumeration.
    Represents time in seconds.
    """

    s = 1
    ms = 1e-3
    us = 1e-6


@dataclass
class Channel:
    """Channel dataclass."""

    number: int
    name: str

    vert_range: int = 1
    vert_range_unit: VoltBase = VoltBase.V

    offset: int = 0
    offset_unit: VoltBase = VoltBase.V

    probe_ratio: ProbeRatio = ProbeRatio.RATIO_1

    def __post_init__(self):
        """Post-initialization processing."""
        if not isinstance(self.number, int) or self.number <= 0 or self.number > 4:
            raise ValueError("ID must be a positive integer between 1 and 4.")
        if not isinstance(self.name, str) or not self.name or len(self.name) >= 10:
            raise ValueError(
                "Name must be a non-empty string, with less than 10 character."
            )

        if not isinstance(self.vert_range, int) or self.vert_range <= 0:
            raise ValueError("Vertical range must be a positive integer.")
        if not isinstance(self.vert_range_unit, VoltBase):
            raise ValueError("Vertical range unit must be an instance of RangeUnit.")
        if not isinstance(self.probe_ratio, ProbeRatio):
            raise ValueError("Probe ratio must be an instance of ProbeRatio.")
        if not isinstance(self.offset, int):
            raise ValueError("Offset must be an integer.")
        if not isinstance(self.offset_unit, VoltBase):
            raise ValueError("Offset unit must be an instance of RangeUnit.")

        # Convert offset and vertical range to the same unit for comparison
        offset_in_volts = self.offset / self.offset_unit.value
        vert_range_in_volts = self.vert_range / self.vert_range_unit.value
        if abs(offset_in_volts) > vert_range_in_volts:
            raise ValueError("Offset must be within the range of ±vert_range.")


@dataclass
class Trigger:
    """Trigger dataclass."""

    src: TriggerSrc = TriggerSrc.EXTERNAL
    slope: SlopeType = SlopeType.POSITIVE

    threshold: int = 1
    threshold_unit: VoltBase = VoltBase.V

    def __post_init__(self):
        """Post-initialization processing."""
        if not isinstance(self.src, TriggerSrc):
            raise ValueError("Trigger name must be an instance of TriggerSrc.")
        if not isinstance(self.slope, SlopeType):
            raise ValueError("Slope must be an instance of TriggerSlope.")
        if not isinstance(self.threshold, (int, float)) or self.threshold <= 0:
            raise ValueError("Trigger threshold must be a positive number.")
        if not isinstance(self.threshold_unit, VoltBase):
            raise ValueError("Trigger threshold unit must be an instance of RangeUnit.")


@dataclass
class KeysightConfig:
    """Keysight configuration dataclass."""

    channels: List[Channel]
    trigger: Trigger

    hor_range: int = 100
    hor_range_unit: TimeBase = TimeBase.ms

    frequency: int = 1
    frequency_unit: FreqBase = FreqBase.H

    def __post_init__(self):
        """Post-initialization processing."""
        if (
            not isinstance(self.channels, list)
            or not self.channels
            or not all(isinstance(ch, Channel) for ch in self.channels)
        ):
            raise ValueError("Channels must be a list of Channel instances.")
        if not isinstance(self.trigger, Trigger):
            raise ValueError("Trigger must be an instance of Trigger.")
        if not isinstance(self.frequency, int) or self.frequency <= 0:
            raise ValueError("Frequency must be a positive integer.")
        if not isinstance(self.frequency_unit, FreqBase):
            raise ValueError("Frequency unit must be an instance of FreqUnit.")
        if not isinstance(self.hor_range, int) or self.hor_range <= 0:
            raise ValueError("Horizontal range must be a positive integer.")
        if not isinstance(self.hor_range_unit, TimeBase):
            raise ValueError("Horizontal range unit must be an instance of TimeBase.")
