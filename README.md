# israelseas

Homeassistant intergration for Israel beaches weather monitoring.

## Configuration example

``` 
- platform: israelseas
  scan_interval: 00:01:00  
  beaches:
      - Northern Coast
      - Southern Coast
      - Sea of Galilee
      - Gulf of Elat
```

Creates sensor per beach:
- sensor.israelseas_gulf_of_elat
- sensor.israelseas_northern_coast
- sensor.israelseas_sea_of_galilee
- sensor.israelseas_southern_coast

When sensor get correct update it changes status to "Ok", all the data is in sensor attributes:

```
LocationNameEng: Sea of Galilee
LocationNameHeb: ëðøú
LocationId: 211
Sea status: 30
Waves height: 20-40
Waves min: 20
Waves max: 40
Sea temperature: 19
Wind direction: 045-135
Wind speed: 5-15
UVLocationNameEng: Qazrin
UVLocationNameHeb: ÷öøéï
UVLocationId: 201
UVIndex: 0
UVIndexText: None
unit_of_measurement: °C
friendly_name: Sea of Galilee
```

## You are very welcome to add configuration flow

Data collected from [ims.data.gov.il](https://ims.data.gov.il/).
