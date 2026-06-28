# BMW CarData reference material

These are **BMW-provided source artifacts**, kept for reference and used to
generate parts of the integration (e.g. descriptor titles and streaming scopes).
They are not authored by this project and are reproduced here verbatim.

| File | What it is |
| --- | --- |
| `telematics-data-catalogue.txt` | The Telematics Data Catalogue (TDC) — the list of CarData descriptors. Parsed by [`tools/generate_descriptor_titles.py`](../../tools/generate_descriptor_titles.py) and [`scripts/extract_stream_scopes.py`](../../scripts/extract_stream_scopes.py). |
| `bmw-cardata-api-guide.md` | BMW's general CarData API introduction and concepts. |
| `bmw-cardata-api-reference.md` | BMW's CarData REST API endpoint reference. |
| `bmw-cardata-streaming-guide.md` | BMW's CarData MQTT streaming documentation. |
| `customer-api.swagger.json` | OpenAPI/Swagger spec for the CarData customer API. |
| `device-flow.swagger.json` | OpenAPI/Swagger spec for the OAuth device-flow endpoints. |

Authoritative, up-to-date documentation lives at
<https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Introduction>.
