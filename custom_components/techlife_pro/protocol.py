"""Protocol helper for TechLife Pro."""
from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)

# Fixed commands
CMD_ON = b"\xfa\x23\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x23\xfb"
CMD_OFF = b"\xfa\x24\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x24\xfb"

class TechLifeProtocol:
    """Handle TechLife Pro protocol command generation."""

    @staticmethod
    def get_on_command() -> bytes:
        """Get the TURN_ON command."""
        return CMD_ON

    @staticmethod
    def get_off_command() -> bytes:
        """Get the TURN_OFF command."""
        return CMD_OFF

    @staticmethod
    def get_brightness_command(brightness: int) -> bytes:
        """
        Generate brightness command.
        
        Based on reverse engineering:
        Structure: \x28 + ... + brightness_byte + ... + checksum + \x29
        
        The exact checksum algorithm is complex/unknown, but fixed patterns have been found.
        We will use a best-effort approximation or look-up for common values if needed.
        However, based on '10% = 0x64 (100 decimal?? no 0x64 is 100)' wait.
        
        Re-checking research:
        10% Brightness: \x28...\x64...\x95\x29  (0x64 = 100) -> Maybe internal scale is 0-1000? or 0-100?
        100% Brightness: \x28...\x11\x27...\xa2\x29 (0x1127 = 4391??) - This seems odd.
        
        Let's look at the patterns usually found in similar devices (MagicHome etc).
        
        Actually, for this specific request, since we don't have the EXACT algorithm,
        and the user knows this is "approximate" or "based on research",
        we might be better off just using ON/OFF for now if the brightness logic is too unstable,
        OR implement a simple mapping if we had enough data points.
        
        Given the limited data points from search (10, 25, 50, 75, 100),
        we can implement a 'nearest neighbor' lookup to be safe.
        This guarantees we send valid known commands.
        """
        # Known points: brightness (0-255) -> command
        # 10% (25) -> ...
        # 25% (64) -> ...
        # 50% (128) -> ...
        # 75% (191) -> ...
        # 100% (255) -> ...
        
        # We will map input brightness 0-255 to the closest known level to ensure stability.
        
        b_percent = (brightness / 255.0) * 100
        
        if b_percent <= 10:
             return b"\x28\x00\x00\x00\x00\x00\x00\x64\x00\x00\x00\x00\x01\xf0\x95\x29" # 10%
        elif b_percent <= 35:
             return b"\x28\x00\x00\x00\x00\x00\x00\x36\x04\x00\x00\x00\x0a\xf0\xc8\x29" # 25%
        elif b_percent <= 60:
             return b"\x28\x00\x00\x00\x00\x00\x00\x23\x0e\x00\x00\x00\x24\xf0\xf9\x29" # 50%
        elif b_percent <= 85:
             return b"\x28\x00\x00\x00\x00\x00\x00\x89\x14\x00\x00\x00\x34\xf0\x59\x29" # 75%
        else:
             return b"\x28\x00\x00\x00\x00\x00\x00\x11\x27\x00\x00\x00\x64\xf0\xa2\x29" # 100%
