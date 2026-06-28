<p align="center">
  <img src="logo.png" alt="BMW CarData (HA) logo" width="240" />
</p>

# BMW CarData (HA)

A Home Assistant integration for the **BMW CarData** MQTT stream and REST API.
It subscribes to the CarData stream, keeps the OAuth tokens fresh, and turns
every descriptor into a native sensor or binary sensor. It also polls the REST
API for telematics, basic vehicle data, charging history, tyre diagnosis,
location-based charging settings, and the vehicle image — all within BMW's
**50 requests / 24h** quota.

> ⚠️ **Experimental.** Built for personal use and tested on a small set of
> vehicles (2022 i4, 2016 i3) and an older HA instance. Don't rely on it for
> critical automations yet. The `beta` branch may be broken at any time — use
> `main`.

> **Credit:** A fork and continuation of the public-domain
> [`bmw-cardata-ha`](https://github.com/JjyKsi/bmw-cardata-ha) by **JjyKsi**.
> See [`NOTICE`](NOTICE).

## Requirements

- A BMW CarData account with **CarData API** and **CarData Streaming** subscribed
  in the BMW portal, plus a generated **client ID**.
- Home Assistant **2024.6** or newer.
- Familiarity with [BMW's CarData documentation](https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Introduction).

## BMW portal setup (do this first)

The CarData web portal isn't available in every market (e.g. it's disabled in
Finland), but you can log in via any supported region — the generated client ID
and configuration are shared across all of them.

- **BMW:** [English](https://www.bmw.co.uk/en-gb/mybmw/vehicle-overview) · [German](https://www.bmw.de/de-de/mybmw/vehicle-overview)
- **Mini:** [English](https://www.mini.co.uk/en-gb/mymini/vehicle-overview) · [German](https://www.mini.de/de-de/mymini/vehicle-overview)

1. Select the vehicle you want to stream and choose **BMW CarData** / **Mini CarData**.
2. [Generate a client ID](https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Technical-registration_Step-1).
3. Subscribe the client to both scopes — `cardata:api:read` and
   `cardata:streaming:read` — and authorize.
   *If the portal shows a scope-selection error, reload, pick one scope, wait
   ~30 s, then add the other.*
4. In **Data Selection** (`Datenauswahl ändern`), click "Load more" until all
   descriptors are listed, then check the ones you want to stream. To select all
   visible descriptors, open the browser console and run:

   ```js
   (() => {
     const labels = document.querySelectorAll('.css-k008qs label.chakra-checkbox');
     let changed = 0;
     labels.forEach(label => {
       const input = label.querySelector('input.chakra-checkbox__input[type="checkbox"]');
       if (!input || input.disabled || input.checked) return;
       label.click();
       if (!input.checked) {
         const ctrl = label.querySelector('.chakra-checkbox__control');
         if (ctrl) ctrl.click();
       }
       if (!input.checked) {
         input.checked = true;
         ['click', 'input', 'change'].forEach(type =>
           input.dispatchEvent(new Event(type, { bubbles: true }))
         );
       }
       if (input.checked) changed++;
     });
     console.log(`Checked ${changed} of ${labels.length} checkboxes.`);
   })();
   ```

   For the **Extrapolated SOC** helper sensors, make sure the container includes
   `vehicle.drivetrain.batteryManagement.header`,
   `vehicle.drivetrain.batteryManagement.maxEnergy`,
   `vehicle.powertrain.electric.battery.charging.power`, and
   `vehicle.drivetrain.electricEngine.charging.status`.
5. Save the selection and repeat for every car you want to support.

## Installation (HACS)

1. Add this repository to HACS as a **custom repository** (type: Integration).
2. Install **BMW CarData (HA)** from the Custom section.
3. Restart Home Assistant.

## Configuration

1. **Settings → Devices & Services → Add Integration → BMW CarData (HA)**.
2. The first screen walks you through the BMW portal setup and asks for your
   **client ID**.
3. Home Assistant then shows an **authorization link** and a code. Open the
   link, sign in, and approve the device on BMW's site. The dialog waits and
   **continues automatically** the moment you approve — there's nothing to click
   in HA, and nothing to time. If approval times out or is declined, press
   **Submit** to get a fresh code and retry.
4. Wait for the car to send data; triggering an action in the MyBMW app
   (lock/unlock) usually produces an update immediately.

If BMW later rejects the token, use **Configure → Re-authorize with BMW**.
Removing and re-adding the integration with the same client ID also works — the
old entry is deleted automatically.

> Moving from the original `cardata` integration? Entity IDs changed with the
> rebrand. Remove the old install first — see [docs/clean-install.md](docs/clean-install.md).

## Entities

- Each VIN becomes a device (VIN pulled from CarData).
- Sensors and binary sensors are auto-created and named from descriptors
  (e.g. `Cabin Door Row1 Driver Is Open`). Friendly names are generated from the
  BMW catalogue — see [`descriptor_titles.py`](custom_components/bmw_cardata/descriptor_titles.py)
  and open an issue/PR if a name looks wrong.
- Distance sensors use `device_class: distance`; odometer/mileage uses
  `state_class: total_increasing` for long-term statistics.
- Each entity carries the source timestamp as an attribute.

## Services

Available under Developer Tools and as buttons in the integration's **Configure**
menu. **Each call counts against the 50 requests / 24h quota.**

| Service | Description |
| --- | --- |
| `bmw_cardata.fetch_telematic_data` | Current contents of the telematics container for a VIN. |
| `bmw_cardata.fetch_vehicle_mappings` | `GET /customers/vehicles/mappings` (PRIMARY/SECONDARY status). |
| `bmw_cardata.fetch_basic_data` | Static metadata (model, series, …) for a VIN. |
| `bmw_cardata.fetch_charging_history` | Charging sessions (paginated; optional `from`/`to`). |
| `bmw_cardata.fetch_tyre_diagnosis` | Smart-maintenance tyre diagnosis. |
| `bmw_cardata.fetch_location_charging_settings` | Location-based charging settings (paginated). |
| `bmw_cardata.fetch_vehicle_image` | Vehicle image. |

## Debug logging

Off by default. Enable via **Configure → options** (`debug_log`) or by setting
`DEBUG_LOG = True` in [`const.py`](custom_components/bmw_cardata/const.py), then
reload. Debug logs are verbose and may contain vehicle data (GPS, VIN) — keep
them off unless troubleshooting.

## Known limitations

- Only one BMW stream per GCID — no other client can be connected at the same time.
- The CarData API is read-only; this integration cannot send commands to the car.
- Clicking Continue in the config flow before approving on BMW's site stalls the
  device-code flow; cancel and restart.

## Issues & discussion

- Bugs in this integration → [Issues](https://github.com/JustChr/HABMW-CarData/issues).
- BMW-side registration problems, setup help, general questions →
  [Discussions](https://github.com/JustChr/HABMW-CarData/discussions).

## License

Licensed under the [MIT License](LICENSE). The original project was released into
the public domain, which allows this relicensing; the original author is credited
in [`NOTICE`](NOTICE) as a courtesy.

"BMW", "Mini", "Rolls-Royce", and "CarData" are trademarks of their respective
owners. This is an independent, community-built integration and is **not**
affiliated with, endorsed by, or sponsored by BMW Group. Use at your own risk;
see the warranty disclaimer in the LICENSE.
