"""The IsraelSeas component."""
from homeassistant.core import Config, HomeAssistant

from .config_flow import IsrSeasFlowHandler  
from .const import DOMAIN  


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured IsraelSeas."""
    return True


async def async_setup_entry(hass, config_entry):
    """Set up IsraelSeas as config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "israelseas"),
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(config_entry, "israelseas")
    return True
