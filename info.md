# BMW CarData (HA)

Turn your BMW CarData stream into native Home Assistant entities. This
integration subscribes directly to the BMW CarData MQTT stream, keeps the OAuth
tokens fresh automatically, and creates sensors / binary sensors for every
descriptor that emits data. It also polls the CarData REST API for telematics,
basic vehicle data, charging history, tyre diagnosis, location-based charging
settings and the vehicle image — all within BMW's 50 requests / 24h quota.

## Requirements

- A BMW CarData account with **CarData API** + **CarData Streaming** subscribed
  in the BMW portal, and a generated **client ID**.
- Home Assistant 2024.6 or newer.

## Setup

1. Add the integration via **Settings → Devices & Services → Add Integration →
   BMW CarData (HA)**.
2. Enter your client ID and complete the BMW Device Code authorization.
3. Wait for the car to send data (locking/unlocking via the MyBMW app usually
   triggers an update).

See the [README](https://github.com/JustChr/HABMW-CarData) for the full BMW
portal setup, descriptor selection helper, and troubleshooting.

---

This project is a fork of the public-domain
[`bmw-cardata-ha`](https://github.com/JjyKsi/bmw-cardata-ha) by **JjyKsi** and is
distributed under the MIT License. It is an independent community integration and
is not affiliated with or endorsed by BMW Group.
