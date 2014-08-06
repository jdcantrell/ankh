'''Ankh - will parse a template with {{http://somewhere/rss/feed|fn}} tags
fetching the feeds and running the function on each item in the feed'''
import argparse
import sys
import os
import codecs
import time
import re
import hashlib

from jinja2 import Environment, FileSystemLoader
import feedparser
import requests

from noa import noa

'''Because jinja parses the template once when loaded and again when
rendered, use a global flag to see if we should actually bother to
fetch/load urls'''
PARSE_URLS = False

def _get_feed(url):
  if PARSE_URLS:
    md5 = hashlib.md5()
    md5.update(url)

    cache_file = '%s/%s' % (options.cache_path, md5.hexdigest())

    if options.cache and os.path.exists(cache_file):
      if options.verbose:
        print "Loading from cache: %s" % url
      cache_fh = open(cache_file, 'r')
      data = cache_fh.read()
      cache_fh.close()
    else:
      if options.verbose:
        print "Fetching: %s" % url
      data = url
      if options.cache:
        r = requests.get(url);
        data = r.text
        cache_fh = codecs.open(cache_file, "w", "utf-8")
        cache_fh.write(data)
        cache_fh.close()

    return feedparser.parse(data)
  else:
    return []

def feed(url, count = 5):
  feed = _get_feed(url)
  return feed.entries[0:count]

def find_link(text, index = 0):
  urls = re.findall(r'href="([^"]+)"', text)
  return urls[index]

def weathers(latlngs):
  data = []
  for lat, lng in latlngs:
    data.append(noa(lat, lng))

  return data

def time_sort(urls):
    '''Display the entry with time posted prefixed'''
    entries = []
    time_list = {}
    for url in urls:
      feed = _get_feed(url)

      if len(feed.entries):
        entry = feed.entries[0]
        entry.feed_title = feed.feed.title.split('-')[0]

        try:
          published = entry.date_parsed
        except AttributeError:
          try:
            published = entry.updated_parsed
          except AttributeError:
            try:
              published = entry.published_parsed
            except AttributeError:
              published = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        ago = time.mktime(time.localtime()) - time.mktime(published)
        #unique key
        while time_list.has_key(ago):
          ago += .1

        time_list[ago] = True;

        entry.time_raw = ago
        if ago < 3600:
          entry.time_length = 0
          entry.time_unit = 'New!'
        elif ago < 43200:
          entry.time_length = int(round(ago / 3600))
          entry.time_unit = 'hour'
        elif ago < 2419200:
          entry.time_length = int(round(ago / 86400))
          entry.time_unit = 'day'
        else:
          entry.time_length = int(round(ago / 2419200))
          entry.time_unit = 'month'

        if entry.time_length > 1:
          entry.time_unit += 's'

        entries.append(entry)

    if len(entries):
      return sorted(entries, key = lambda k: k.time_raw)
    else:
      return []

def main():
  full_path = os.path.abspath(options.template)
  path = os.path.dirname(full_path)

  env = Environment(loader=FileSystemLoader(path))

  env.filters['feed'] = feed
  env.filters['find_link'] = find_link
  env.filters['time_sort'] = time_sort
  env.filters['weathers'] = weathers

  global PARSE_URLS
  PARSE_URLS = False

  print "Loading %s" % options.template
  template = env.get_template(full_path.replace(path + '/', ""))


  print "Rendering..."

  PARSE_URLS = True
  html = template.render()
  outfile = codecs.open(options.outfile, "w", "utf-8")
  outfile.write(html)
  outfile.close()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--template", dest="template", \
    help="Template file to load. Defaults to ankh.template", \
    default="ankh.template")
  parser.add_argument("-o", "--outfile", dest="outfile", \
    help="File to save the parsed template and feeds to. Defaults to \
    ankh.html", default="ankh.html")
  parser.add_argument("-v", "--verbose", dest="verbose", \
    help="Be verbose about what is going on", action="store_true",
    default=False)
  parser.add_argument("-c", "--cache", dest="cache", \
    help="Cache feeds", action="store_true",
    default=False)
  parser.add_argument("--cache_path", dest="cache_path", \
    help="The directory to store cache files", default="./ankh_cache")


  global options
  options = parser.parse_args()

  if options.cache:
    if not os.path.exists(options.cache_path):
      os.makedirs(options.cache_path)
  main()
