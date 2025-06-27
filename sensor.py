import json
import xmltodict
import logging
import requests
from datetime import timedelta
from datetime import datetime
from jsonpath import jsonpath
from requests import Session
import voluptuous as vol
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from const import CONF_RAD_RESOURCE, CONF_TEMP_RESOURCE

"""Platform for sensor integration."""
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.components.sensor import PLATFORM_SCHEMA, ENTITY_ID_FORMAT
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    LOCATIONS_MAP,
    UVINDEX_MAP,
    ICONWAVES_MAP
)

_LOGGER = logging.getLogger(__name__)

CONF_BEACHES = 'beaches'

class DataLoader():

    def __init__(self, rad_resource, temp_resource):
        """Initialize the sensor."""
        self._state = None
        self._attributes = None
        self._http_session = Session()
        self._headers = {}
        self._auth = ""
        self._request_data = ""
        self._timeout = 10000
        self._verify_ssl = True
        self._lastUpdate = datetime.now()
        self._radResource = rad_resource
        self._tempResource = temp_resource
        _LOGGER.debug("LOCATIONS_MAP: {0}".format(LOCATIONS_MAP))


    def getUVIndexes(self):
        _LOGGER.debug("-->getUVIndexes   Updating from %s", self._radResource)   
        try:
            response = self._http_session.request(
                'GET',
                self._radResource,
                headers=self._headers,
                auth=self._auth,
                data=self._request_data,
                timeout=self._timeout,
                verify=self._verify_ssl,
            )
            """response.encoding = 'utf-8'"""
            _LOGGER.debug("Response code: %s %s", response.status_code, response.reason)
            self.data = response.text
            self.headers = response.headers
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("getUVIndexes failed to fetch data: %s failed with %s", self._resource, ex)
            self.headers = None
        
        """value = json.dumps(xmltodict.parse(response.text))
        json_dict = json.loads(value)"""       
        json_dict = xmltodict.parse(response.text)
        """locationsList = jsonpath(json_dict, '$...Location[?(@.LocationMetaData.LocationId==500|518|402|115|201)]')"""
        locationsList = jsonpath(json_dict, '$...Location[*]')
        locationsData = {};

        current_datetime = datetime.now()      
        
        for location in locationsList:
            locationId = location.get('LocationMetaData').get('LocationId')
            if locationId in LOCATIONS_MAP.keys():
                locationNameEng = location.get('LocationMetaData').get('LocationNameEng')
                locationNameHeb = location.get('LocationMetaData').get('LocationNameHeb')
                locationData = {'UVLocationNameEng' : locationNameEng, "UVLocationNameHeb" : locationNameHeb, "UVLocationId" : locationId};
                
                """ find elemnt that corresonds to current datetime"""
                currentTimeIndex = -1;
                for i in range(len(location.get('LocationData').get('TimeUnitData'))) :
                   elementPeriodStart = location.get('LocationData').get('TimeUnitData')[i].get('SolRadPeriod').get('DateTimeFrom')
                   elementPeriodStartDt = datetime.strptime(elementPeriodStart, '%Y-%m-%d %H:%M')
                   elementPeriodEnd = location.get('LocationData').get('TimeUnitData')[i].get('SolRadPeriod').get('DateTimeTo')
                   elementPeriodEndDt = datetime.strptime(elementPeriodEnd, '%Y-%m-%d %H:%M')
                   _LOGGER.debug("periodIndex: %s  current_datetime: %s    elementPeriodStartDt: %s elementPeriodEndDt: %s", i, current_datetime,elementPeriodStartDt, elementPeriodEndDt)
                   if (current_datetime > elementPeriodStartDt and current_datetime < elementPeriodEndDt):
                        currentTimeIndex = i
                        break
                   
                _LOGGER.warning("currentTimeIndex: %s", currentTimeIndex)
                
                if currentTimeIndex == -1:
                   locationData['UVIndex'] = '0'
                   locationData['UVIndexText'] = 'None'                
                else:
                   locationDataElementList = location.get('LocationData').get('TimeUnitData')[currentTimeIndex].get('Element')
                   elementValue = locationDataElementList.get('ElementIndex')
                   locationData['UVIndex'] = elementValue
                   translatedValue = UVINDEX_MAP.get(locationDataElementList.get('ElementValue'))
                   locationData['UVIndexText'] = translatedValue
                locationsData[locationId] = locationData
        decode = json.dumps(locationsData)
        """_LOGGER.debug("{0}".format(decode))"""
        return locationsData


    def getTemperatures(self):
        _LOGGER.debug("-->getTemperatures   Updating from %s", self._tempResource)
        try:
            response = self._http_session.request(
                'GET',
                self._tempResource,
                headers=self._headers,
                auth=self._auth,
                data=self._request_data,
                timeout=self._timeout,
                verify=self._verify_ssl,
            )
            _LOGGER.debug("Response code: %s %s", response.status_code, response.reason)
            self.data = response.text
            self.headers = response.headers
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("getTemperatures failed to fetch data: %s failed with %s", self._resource, ex)
            self.headers = None
        
        json_dict = xmltodict.parse(response.text)
        locationsList = jsonpath(json_dict, '$...Location[*]')
        locationsData = {};
        for location in locationsList:
            locationId = location.get('LocationMetaData').get('LocationId')
            locationNameEng = location.get('LocationMetaData').get('LocationNameEng')
            locationNameHeb = location.get('LocationMetaData').get('LocationNameHeb')
            locationData = {'LocationNameEng' : locationNameEng, "LocationNameHeb" : locationNameHeb, "LocationId" : locationId};
            locationDataElementList = location.get('LocationData').get('TimeUnitData')[0].get('Element')
            for element in locationDataElementList:
                elementName = element.get('ElementName')
                elementValue = element.get('ElementValue')
                if elementName == 'Sea status and waves height' :
                    elementValues = elementValue.split('/')
                    locationData['Sea condition'] = elementValues[0].strip()
                    locationData['Waves height'] = elementValues[1].strip()
                    waves = locationData['Waves height'].split('-')
                    locationData['Waves min'] = waves[0].strip()
                    locationData['Waves max'] = waves[1].strip()
                elif elementName == 'Wind direction and speed' :
                    elementValues = elementValue.split('/')
                    locationData['Wind direction'] = elementValues[0].strip()
                    locationData['Wind speed'] = elementValues[1].strip()
                else :
                    locationData[elementName] = elementValue
            locationsData[locationNameEng] = locationData;
        decode = json.dumps(locationsData)
        """_LOGGER.debug("{0}".format(decode))"""
        return locationsData

    def update(self):
        """Fetch new state data for the sensor"""
        if (self._lastUpdate < datetime.now() - timedelta(seconds = 10)) :
            _LOGGER.debug("DataLoader.update")
            self._lastUpdate = datetime.now()
            attrs = {}            
            locationsData = self.getTemperatures()
            uvlocationsData = self.getUVIndexes()
            """_LOGGER.debug("uvlocationsData: {0}".format(uvlocationsData))"""
            for element in uvlocationsData:
                if uvlocationsData[element].get("UVLocationId") in LOCATIONS_MAP.keys():
                    translatedName = LOCATIONS_MAP.get(uvlocationsData[element].get("UVLocationId"))
                    if translatedName in locationsData.keys():
                        """_LOGGER.debug("tempData: {0}".format(locationsData.get(translatedName)))"""
                        """_LOGGER.debug("uvData: {0}".format(uvlocationsData[element]))"""
                        locationsData.get(translatedName).update(uvlocationsData[element])
                        """_LOGGER.debug("resultData: {0}".format(locationsData[translatedName]))"""
            attrs = locationsData
            self._attributes = attrs
            self._state = 'Ok'



# _DATALOADER = DataLoader()
ISRAELBEACHES = ['Northern Coast', 'Southern Coast', 'Sea of Galilee','Gulf of Elat']
DEFAULT_NAME = 'IsraelSeas'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(DOMAIN, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_BEACHES, default=[]):
        vol.All(cv.ensure_list, [vol.In(ISRAELBEACHES)])      
})


# def setup_platform(hass, config, add_entities, discovery_info=None):
#     name = config.get(DOMAIN)
#     dev = []
#     for beach in config[CONF_BEACHES]:
#         _LOGGER.debug('{} setup: {}'.format(DOMAIN,beach))
#         uid = '{}_{}'.format("israelseas", beach)
#         entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)
#         dev.append(IsraelSeasSensor(entity_id, beach))
#     add_entities(dev, True)

async def async_setup_entry(hass, config_entry, async_add_entities):
    rad_resource = config_entry.options.get(CONF_RAD_RESOURCE, config_entry.data.get(CONF_RAD_RESOURCE))
    temp_resource = config_entry.options.get(CONF_TEMP_RESOURCE, config_entry.data.get(CONF_TEMP_RESOURCE))
    beaches = config_entry.data.get(CONF_BEACHES, [])

    data_loader = DataLoader(rad_resource, temp_resource)

    dev = []
    for beach in beaches:
        uid = f"israelseas_{beach}"
        entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)
        dev.append(IsraelSeasSensor(entity_id, beach, data_loader))

    async_add_entities(dev, True)




class IsraelSeasSensor(Entity):

    def __init__(self, entity_id, name, data_loader):
        """Initialize the sensor."""
        self.entity_id = entity_id
        self._state = None
        self._attributes = {}
        self._name = name
        self._data_loader = data_loader

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS


    def update(self):
        self._data_loader.update()
        if (self._data_loader._attributes is not None):
            self._state = self._data_loader._attributes[self._name]["Sea temperature"]
            self._attributes = self._data_loader._attributes[self._name]
            for waveSize in ICONWAVES_MAP.keys():
                if (int(self._state) < waveSize):
                    self._attributes['icon'] = ICONWAVES_MAP[waveSize]
                    break
        return self._state;


    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        """return {
                **{'aaaa': 'aaaaaazzzz'},
                **self._attributes,
                ATTR_ATTRIBUTION: 'bbb',
            }"""
        
        return self._attributes
