'''Ankh - will parse a template with {{http://somewhere/rss/feed|fn}} tags
fetching the feeds and running the function on each item in the feed'''
import argparse
import os
import codecs
import time
import re

from jinja2 import Environment, FileSystemLoader
import feedparser

def feed(url, count = 5):
  if options.verbose:
    print "Parsing %s" % url
  feed = feedparser.parse(url)
  return feed.entries[0:count]

def find_link(text, index = 0):
  urls = re.findall(r'href="([^"]+)"', text) 
  return urls[index]

def time_sort(urls):
    '''Display the entry with time posted prefixed'''
    entries = []
    time_list = {}
    for url in urls:
      if options.verbose:
        print "Parsing %s" % url

      feed = feedparser.parse(url)
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
  env = Environment(loader=FileSystemLoader(os.getcwd()));

  env.filters['feed'] = feed
  env.filters['find_link'] = find_link
  env.filters['time_sort'] = time_sort

  template = env.get_template(options.template);

  outfile = codecs.open(options.outfile, "w", "utf-8")
  outfile.write(template.render())

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

  global options
  options = parser.parse_args()
  main()
