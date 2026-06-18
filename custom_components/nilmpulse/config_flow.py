import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_P1_SENSOR

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="NILMpulse AI Engine", data=user_input)

        # Haal alle beschikbare notificatie-entiteiten op die met 'notify.mobile_app_' beginnen
        notify_entities = [
            entity_id for entity_id in self.hass.states.async_entity_ids("notify")
            if "mobile_app" in entity_id
        ]

        data_schema = vol.Schema({
            vol.Required(CONF_P1_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),
            vol.Optional("notification_device"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=notify_entities,
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
