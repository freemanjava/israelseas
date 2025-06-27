"""Config flow to configure IsraelSeas component."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_RAD_RESOURCE, CONF_TEMP_RESOURCE


@callback
def configured_instances(hass):
    """Return a set of configured SimpliSafe instances."""
    entries = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        entries.append(DOMAIN)
    return set(entries)


class IsrSeasFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Met component."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Init IsrSeasFlowHandler."""
        self._errors = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return IsraelSeasOptionsFlowHandler(config_entry)


    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            if (
                f"{user_input.get('CONF_LATITUDE')}-{user_input.get('CONF_LONGITUDE')}"
                not in configured_instances(self.hass)
            ):
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
            self._errors[CONF_NAME] = "name_exists"

        return await self._show_config_form(
            name=DOMAIN
        )

    async def _show_config_form(
        self, name=None, latitude=None, longitude=None, elevation=None
    ):
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=name): str,
                    vol.Required(CONF_RAD_RESOURCE, default="https://ims.data.gov.il/sites/default/files/isr_rad.xml"): str,
                    vol.Required(CONF_TEMP_RESOURCE, default="https://ims.data.gov.il/sites/default/files/isr_sea.xml"): str
                }
            ),
            errors=self._errors,
        )

    async def async_step_onboarding(self, data=None):
        """Handle a flow initialized by onboarding."""
        return self.async_create_entry(
            title=HOME_LOCATION_NAME, data={CONF_TRACK_HOME: True}
        )

class IsraelSeasOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_RAD_RESOURCE,
                    default=self.config_entry.options.get(
                        CONF_RAD_RESOURCE,
                        self.config_entry.data.get(CONF_RAD_RESOURCE, "https://ims.data.gov.il/sites/default/files/isr_rad.xml")
                    ),
                ): str,
                vol.Required(
                    CONF_TEMP_RESOURCE,
                    default=self.config_entry.options.get(
                        CONF_TEMP_RESOURCE,
                        self.config_entry.data.get(CONF_TEMP_RESOURCE, "https://ims.data.gov.il/sites/default/files/isr_sea.xml")
                    ),
                ): str,
            }),
        )

