# Clean install — BMW CarData (HA) residual artifacts

This note documents every file, registry entry, and flag the BMW CarData integration can create. Use it when you want to fully clean your Home Assistant instance before testing a fresh install.

## Config Entry Data

The integration stores runtime state directly on the config entry. Expect these keys to persist until the entry is removed:

- `client_id`, `access_token`, `refresh_token`, `id_token`, `expires_in`, `scope`, `gcid`, `token_type`, `received_at`
- Bootstrap and runtime flags: `bootstrap_complete`, `vin`, `last_telematic_poll`
- HV container info: `hv_container_id`, `hv_descriptor_signature`
- Cached vehicle metadata: `vehicle_metadata`

Options (if ever set through the hidden overrides view): `mqtt_keepalive`, `diagnostic_log_interval`, `debug_log`.

Removing the integration deletes the config entry, but the related devices/entities described below may remain.

## .storage Files

- `bmw_cardata_<entry_id>_request_log`: rolling API quota log written via `homeassistant.helpers.storage.Store`. These JSON files are left behind unless you delete them manually. (Installs migrated from the original `cardata` integration may also leave a `cardata_<entry_id>_request_log` file behind.)

## Device Registry

- One integration-level device: `("bmw_cardata", <entry_id>)` named "CarData Debug Device".
- One device per VIN: `("bmw_cardata", <vin>)` populated with metadata from basic vehicle data or stream payloads.

Delete both from *Settings → Devices & Services → Devices* if you want a clean slate.

## Entity Registry

Entities are created dynamically from stream/telematics data and remain after removal unless manually deleted.

- Sensor descriptors (`sensor.<vin>_*`) for non-boolean data.
- Binary descriptors (`binary_sensor.<vin>_*`) for boolean data.
- Diagnostics sensors: `sensor.cardata_debug_connection_status`, `sensor.cardata_debug_last_message`, `sensor.cardata_debug_last_telematic_api`.
- SOC helpers per VIN: `sensor.<vin>_soc_estimate`, `sensor.<vin>_soc_rate`.

Disable or remove these from *Settings → Devices & Services → Entities* as needed.

## Services & Notifications

- Services registered while any entry is loaded: `bmw_cardata.fetch_telematic_data`, `bmw_cardata.fetch_vehicle_mappings`, `bmw_cardata.fetch_basic_data`, `bmw_cardata.fetch_charging_history`, `bmw_cardata.fetch_tyre_diagnosis`, `bmw_cardata.fetch_location_charging_settings`, `bmw_cardata.fetch_vehicle_image`. They vanish automatically once the last entry unloads.
- Reauthentication failures raise a persistent notification with id `bmw_cardata_reauth_<entry_id>` that must be dismissed manually if still visible.

## Runtime Cache

While loaded, runtime data sits in `hass.data["cardata"][<entry_id>]` (stream manager, session, quota manager, etc.). This disappears after unloading, but it is useful to know when debugging.

## Fresh Install Checklist

1. Remove the Cardata integration from the UI.
2. Delete lingering devices (debug device and per-VIN devices).
3. Delete lingering entities (descriptor sensors, binary sensors, diagnostics, SOC sensors).
4. Remove `custom_components.cardata_*_request_log` files from `.storage`.
5. Dismiss any remaining reauth notifications.

After these steps, reinstalling Cardata behaves like a true first-time setup.
