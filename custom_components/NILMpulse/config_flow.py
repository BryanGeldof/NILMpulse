import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_P1_SENSOR

class NILMpulseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Beheert de UI Setup Flow voor NILMpulse."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Eerste stap wanneer de gebruiker 'NILMpulse' aanklikt in de UI."""
        errors = {}

        if user_input is not None:
            # Sla de configuratie op en maak de integratie-instantie aan
            return self.async_create_entry(
                title="NILMpulse AI Engine", 
                data=user_input
            )

        # Toon een mooi dropdown-menu in de UI met alle beschikbare stroom-sensoren
        data_schema = vol.Schema({
            vol.Required(CONF_P1_SENSOR): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="power")
            ),
        })

        return self.search_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )
