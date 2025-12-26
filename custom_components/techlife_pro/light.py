"""Platform for TechLife Pro light integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

from .const import DOMAIN
from .protocol import TechLifeProtocol

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the TechLife Pro light platform."""
    
    # We will listen to all dev_pub_+ topics to discover devices
    # and add them dynamically.
    
    discovered_macs = set()

    @callback
    def message_received(msg):
        """Handle new MQTT messages."""
        topic = msg.topic
        # Topic format: dev_pub_{mac}
        try:
            mac = topic.split("_")[-1]
        except IndexError:
            return

        if mac in discovered_macs:
            return

        _LOGGER.info("Discovered TechLife Pro device: %s", mac)
        discovered_macs.add(mac)
        async_add_entities([TechLifeProLight(mac)])

    # Subscribe to discovery topic
    await mqtt.async_subscribe(hass, "dev_pub_+", message_received)


class TechLifeProLight(LightEntity):
    """Representation of a TechLife Pro Light."""

    _attr_has_entity_name = True
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_color_mode = ColorMode.BRIGHTNESS

    def __init__(self, mac: str) -> None:
        """Initialize the light."""
        self._mac = mac
        self._attr_unique_id = slugify(f"techlife_{mac}")
        self._attr_name = f"TechLife Strip {mac}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=f"TechLife Strip {mac}",
            manufacturer="TechLife",
            model="Pro LED Strip",
        )
        self._cmd_topic = f"dev_sub_{mac}"
        self._state_topic = f"dev_pub_{mac}"
        self._is_on = False
        self._brightness = 255

    async def async_added_to_hass(self) -> None:
        """Subscribe to status updates."""
        await mqtt.async_subscribe(
            self.hass, self._state_topic, self._handle_state_message
        )

    @callback
    def _handle_state_message(self, msg) -> None:
        """Handle status updates."""
        # For now, we assume if we receive a message, the device is online.
        # We don't have enough info to parse the state payload significantly
        # but we can assume availability.
        pass

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self._brightness

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
            cmd = TechLifeProtocol.get_brightness_command(self._brightness)
            await mqtt.async_publish(self.hass, self._cmd_topic, cmd, retain=False, encoding=None)
            self._is_on = True # Brightness command usually turns it on
        else:
            # Just turn on, restore last brightness or full
            await mqtt.async_publish(self.hass, self._cmd_topic, TechLifeProtocol.get_on_command(), retain=False, encoding=None)
            self._is_on = True

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await mqtt.async_publish(self.hass, self._cmd_topic, TechLifeProtocol.get_off_command(), retain=False, encoding=None)
        self._is_on = False
        self.async_write_ha_state()
