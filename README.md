# knmi-precipitation-forecast

KNMI provides precipitation forecast data. This package provides an interface to download and work a bit easier with the Nowcast precipitation forecast data from KNMI.

Nowcast precipitation forecast up to 2 hours ahead, per 5 minutes, over the Netherlands. The forecast contains 25 time steps: +0 minutes to +120 minutes. Forecasted is the precipitation sum per 5 minutes, on a grid of 1x1 km. The forecast is made with an operational KNMI implementation of pySTEPS (https://pysteps.github.io). The forecast is initiated with the KNMI 5-minute real-time precipitation accumulation product: RTCOR-5m.

> More information on the dataset [here](https://dataplatform.knmi.nl/dataset/radar-forecast-2-0)

## Dev

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# To run the notebooks install requirements-dev.txt aswell
pip install -r requirements-dev.txt
```

## KNMI API Key

To use the KNMI data platform you need an API key. You can request one [here](https://developer.dataplatform.knmi.nl/)

## Examples

### Notebooks

See the [notebooks](notebooks) folder for examples.

### Download latest h5 file

Download the latest available h5 file from the KNMI data platform.

```python
from knmi_precipitation.download import OpenDataAPI

api_key = "your-api-key"
oda = OpenDataAPI(api_key)
latest_file = oda.download_latest_file('./data/test.h5')
```

### Get forecast data

Load a .h5 file and get the forecast data in mm/hr and dBZ at a specific location.

```python
from knmi_precipitation.h5_radar_data import H5RadarData

data = H5RadarData('./example_data/RAD_NL25_RAC_FM_202409041355.h5')
lng, lat = 5.319185, 51.687406
value_mm_hr = data.get_mm_hr_from_lon_lat('image1', lng, lat)
```

### Export to GeoTIFF

Export the forecast data of image1 from a .h5 file to a GeoTIFF file warped to EPSG:4326.

```python
from knmi_precipitation.h5_radar_data import H5RadarData

radar = H5RadarData('./example_data/RAD_NL25_RAC_FM_202409041355.h5')
data.export_geotiff('image1', './data/RAD_NL25_RAC_FM_202409041355_1.tif')
```
