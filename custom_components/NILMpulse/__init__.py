from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Instellen van NILMpulse via een UI Config Entry."""
    # Stuur de UI-configuratie door naar het sensor-platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Verwijder de integratie netjes als de gebruiker op 'Verwijderen' klikt in de UI."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
