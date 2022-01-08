"""Constants for Met component."""
import logging

from homeassistant.components.weather import DOMAIN as WEATHER_DOMAIN

DOMAIN = "israelseas"

_LOGGER = logging.getLogger(".")

LOCATIONS_MAP = {'520': 'Gulf of Eilat','518': 'DeadSea', '402': 'Southern Coast', '115': 'Northern Coast', '201': 'Sea of Galilee'}

UVINDEX_MAP = {'L': 'Low', 'M': 'Med', 'H': 'High', 'V': 'Very high', 'E': 'Extreme'}

ICONWAVES_MAP = {100: 'mdi:wave', 999: 'mdi:waves'}