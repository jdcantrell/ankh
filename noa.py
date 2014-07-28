import requests, time
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

    if self.dwml == None:
      self.tree = []
    else:
      self.tree = ET.fromstring(self.dwml)


  def _get_dwml(self):
    url = "http://forecast.weather.gov/MapClick.php?lat=%s&lon=%s&unit=0&lg=english&FcstType=dwml" % (self.lat, self.lng)

    print url

    r = requests.get(url);
    if r.status_code == 200 and r.text.find('javascript') == -1:
      return r.text
    else:
      return None

  def _get_element(self, xpath):
    el = None
    if self.tree != None:
      el = self.tree.find(xpath)

    return el

  def _get_element_text(self, xpath):
    el = self._get_element(xpath)

    if el != None:
      return el.text
    else:
      return None

  def _get_forecast_index(self, index, key_xpath, night = False):
    key_el = self._get_element(key_xpath)
    layout_key = key_el.get('time-layout')

    # if we have a 12hr then we need to double our index and adjust it
    # for it we want the night or day value
    if layout_key.find('p12h'):
      index = index * 2
      if night:
        index += 1


    if self.time_layouts.has_key(layout_key):
      if self.time_layouts[layout_key].has_key(index):
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
          #strip off time zone info
          if idx == 1:
            # TODO: I think hour is always at 6am so if the time is 12am
            # we're going to skip to the next day instead of the current
            # day
            t = time.strptime(time_val.text[0:-6], '%Y-%m-%dT%H:%M:%S')
            #this time layout does not have info for today so skip ahead
            if t > time.gmtime():
              i += 1;
            else:
              if time_val.get('period-name') == 'Tonight' or time_val.get('period-name') == 'Overnight':
                i += 1;
          lut[i] = idx
          idx += 1
          i += 1

        self.time_layouts[key] = lut
      return self._get_forecast_index(index, key_xpath)



  def temp(self):
    xpath = "data/parameters/temperature[@type='apparent']/value"
    return self._get_element_text(xpath)

  def max_temp(self, forecast = 0):
    #0 is todays max temp, if none is returned that means there is no max temp
    index = self._get_forecast_index(forecast, "data/parameters/temperature[@type='maximum']")
    if index != None:
      xpath = "data/parameters/temperature[@type='maximum']/value[%d]" % (index)
      return self._get_element_text(xpath)

    return None

  def min_temp(self, forecast = 0):
    index = self._get_forecast_index(forecast, "data/parameters/temperature[@type='minimum']")
    if index != None:
      xpath = "data/parameters/temperature[@type='minimum']/value[%d]" % (index)
      return self._get_element_text(xpath)
    return None

  def percipitation(self, forecast = 0, night = False):
    index = self._get_forecast_index(forecast, "data/parameters/probability-of-precipitation", night)
    if index != None:
      xpath = 'data/parameters/probability-of-precipitation/value[%d]' % (index)
      return self._get_element_text(xpath)
    return None
    pass

  def condition(self, forecast = 0, night = False):
    index = self._get_forecast_index(forecast, "data/parameters/weather", night)
    if index != None:
      xpath = 'data/parameters/weather/weather-conditions[%d]' % (index)
      el = self._get_element(xpath)
      return el.get('weather-summary')
    return None
    pass



if __name__ == "__main__":
  w = noa(37.9064, -122.065)
  print w.temp()
  print "Today's High: %s" % w.max_temp(0)
  print "Tomorrow's High: %s" % w.max_temp(1)
  print "Today's Min: %s" % w.min_temp(0)
  print "Tomorrow's Min: %s" % w.min_temp(1)

  print "Today's Percipitation %%: %s" % w.percipitation(0, False)
  print "Tomorrow's Percipitation %%: %s" % w.percipitation(1, False)

  print "Today's Condition: %s" % w.condition(0, False)
  print "Tonight's Condition: %s" % w.condition(0, True)
  print "Tomorrow's Condition: %s" % w.condition(1, False)
  print "Tomorrow Night's Condition: %s" % w.condition(1, True)

  print "Tomorrow's Condition: %s" % w.condition(2, False)
  print "Tomorrow Night's Condition: %s" % w.condition(2, True)
