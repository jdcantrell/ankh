import requests

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class noa:
    def __init__(self, latitude, longitude):
        self.lat = latitude
        self.lng = longitude
        self.dwml = self._get_dwml()
        self.time_layouts = {}

        if self.dwml is None:
            self.tree = []
        else:
            self.tree = ET.fromstring(self.dwml)

    def _get_dwml(self):
        url = "http://forecast.weather.gov/MapClick.php?" \
            "lat=%s&lon=%s&unit=0&lg=english&FcstType=dwml" \
            % (self.lat, self.lng)

        r = requests.get(url)
        if r.status_code == 200 and r.text.find('javascript') == -1:
            return r.text
        else:
            return None

    def _get_element(self, xpath):
        el = None
        if self.tree is not None:
            el = self.tree.find(xpath)

        return el

    def _get_element_text(self, xpath):
        el = self._get_element(xpath)

        if el is not None:
            return el.text
        else:
            return None

    def _get_forecast_index(self, index, key_xpath, night=False):
        key_el = self._get_element(key_xpath)
        layout_key = key_el.get('time-layout')

        # if we have a 12hr then we need to double our index and adjust it
        # for it we want the night or day value
        if layout_key.find('p12h') != -1:
            index = index * 2
            if night:
                index += 1

        if layout_key in self.time_layouts:
            if index in self.time_layouts[layout_key]:
                return self.time_layouts[layout_key][index]
            return None
        else:
            layouts = self.tree.findall('data[@type="forecast"]/time-layout')
            for layout in list(layouts):

                key = layout.find('layout-key').text
                lut = {}
                times = layout.findall('start-valid-time')
                idx = 1
                i = 0
                for time_val in times:
                    # strip off time zone info
                    if idx == 1:
                        if time_val.get('period-name') != 'Today':
                            i += 1

                    lut[i] = idx
                    idx += 1
                    i += 1

                self.time_layouts[key] = lut
            return self._get_forecast_index(index, key_xpath)

    def temp(self):
        xpath = "data[@type='current observations']/parameters/" \
            "temperature[@type='apparent']/value"
        return self._get_element_text(xpath)

    def condition(self):
        xpath = "data[@type='current observations']/parameters/" \
            "weather/weather-conditions"
        el = self._get_element(xpath)
        return el.get('weather-summary')

    def dew_point(self):
        xpath = "data[@type='current observations']/parameters/" \
            "temperature[@type='dew point']/value"
        return self._get_element_text(xpath)

    def relative_humidity(self):
        xpath = "data[@type='current observations']/parameters/" \
            "humidity[@type='relative']/value"
        return self._get_element_text(xpath)

    def mbar(self):
        xpath = "data[@type='current observations']/parameters/" \
            "pressure[@type='barometer'][@units='inches of mercury']/value"
        return float(self._get_element_text(xpath)) * 33.8638815

    def forecast_max(self, forecast=0):
        # 0 is todays max temp
        # if none is returned that means there is no max temp
        index = self._get_forecast_index(
            forecast,
            "data/parameters/temperature[@type='maximum']")
        if index is not None:
            xpath = "data/parameters/" \
                "temperature[@type='maximum']/value[%d]" % (index)
            return self._get_element_text(xpath)

        return None

    def forecast_location(self):
        xpath = "data[@type='forecast']/location/description"
        return self._get_element_text(xpath)

    def forecast_min(self, forecast=0):
        index = self._get_forecast_index(
            forecast,
            "data/parameters/temperature[@type='minimum']")
        if index is not None:
            xpath = "data/parameters/" \
                "temperature[@type='minimum']/value[%d]" % (index)
            return self._get_element_text(xpath)
        return None

    def forecast_percipitation(self, forecast=0, night=False):
        index = self._get_forecast_index(
            forecast,
            "data/parameters/probability-of-precipitation",
            night)
        if index is not None:
            xpath = "data/parameters/" \
                "probability-of-precipitation/value[%d]" % (index)
            return self._get_element_text(xpath)
        return None
        pass

    def forecast_condition(self, forecast=0, night=False):
        index = self._get_forecast_index(
            forecast,
            "data/parameters/weather",
            night)
        if index is not None:
            xpath = 'data/parameters/weather/weather-conditions[%d]' % (index)
            el = self._get_element(xpath)
            return el.get('weather-summary')
        return None
        pass


if __name__ == "__main__":
    w = noa(37.9064, -122.065)
    print(w.forecast_location())
    print("Temp: %s" % w.temp())
    print("Conditions: %s" % w.condition())
    print("Dew Point: %s" % w.dew_point())
    print("Relative Humidity: %s%%" % w.relative_humidity())
    print("Pressure: %r mbar" % w.mbar())

    print("Today's High: %s" % w.forecast_max(0))
    print("Tomorrow's High: %s" % w.forecast_max(1))
    print("Today's Min: %s" % w.forecast_min(0))
    print("Tomorrow's Min: %s" % w.forecast_min(1))

    print("Today's Percipitation %%: %s" % w.forecast_percipitation(0, False))
    print("Tomorrow's Percipitation %%: %s" % w.forecast_percipitation(1, False))

    print("Today's Condition: %s" % w.forecast_condition(0, False))
    print("Tonight's Condition: %s" % w.forecast_condition(0, True))
    print("Tomorrow's Condition: %s" % w.forecast_condition(1, False))
    print("Tomorrow Night's Condition: %s" % w.forecast_condition(1, True))

    print("Tomorrow's Condition: %s" % w.forecast_condition(2, False))
    print("Tomorrow Night's Condition: %s" % w.forecast_condition(2, True))

    print("\n---------\n")
    w = noa(45.52, -122.6819)
    print(w.forecast_location())
    print("Temp: %s" % w.temp())
    print("Conditions: %s" % w.condition())
    print("Dew Point: %s" % w.dew_point())

    print("\n---------\n")
    w = noa(43.6167, -116.2)
    print(w.forecast_location())
    print("Temp: %s" % w.temp())
    print("Conditions: %s" % w.condition())
    print("Dew Point: %s" % w.dew_point())

    print("\n---------\n")
    w = noa(38.7453, -94.8292)
    print(w.forecast_location())
    print("Temp: %s" % w.temp())
    print("Conditions: %s" % w.condition())
    print("Dew Point: %s" % w.dew_point())
