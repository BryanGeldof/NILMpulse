from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .analyzer import PeakSenseClusterAnalyzer

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Instellen van NILMpulse via een UI Config Entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        
    # Maak de analyzer aan en hang hem aan de HASS data context
    hass.data[DOMAIN]["analyzer"] = PeakSenseClusterAnalyzer(hass)

    # Stuur de UI-configuratie door naar het sensor-platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Verwijder de integratie netjes als de gebruiker op 'Verwijderen' klikt in de UI."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok and DOMAIN in hass.data:
        hass.data.pop(DOMAIN)
    return unload_ok
