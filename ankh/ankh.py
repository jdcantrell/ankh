"""Ankh - will parse a template with {{http://somewhere/rss/feed|fn}} tags
fetching the feeds and running the function on each item in the feed"""
import os
import codecs
import time
import re
import hashlib
import logging
import io

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import feedparser
import requests
import requests_cache

from .noa import noa

options = {}

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

log_stream = io.StringIO()
log_stream_handler = logging.StreamHandler(log_stream)
logger.addHandler(log_stream_handler)


def _load_url(url):
    try:
        headers = {"User-Agent": "linux:net.goodrobot.ankh:v0.0.1 (by /u/jdcantrell)"}
        r = requests.get(url, timeout=35, headers=headers)
        return r.text
    except requests.exceptions.RequestException as e:
        logger.error("Could not fetch %s" % url)
        logger.error("Exception was raised: %r" % e)

    return ""


def _get_feed(url):
    global options
    data = None

    if data is None:
        if options.verbose:
            print("Fetching: %s" % url)

        data = _load_url(url)

    return feedparser.parse(data)


def _get_date(entry):
    try:
        return entry.date_parsed
    except AttributeError:
        pass

    try:
        return entry.updated_parsed
    except AttributeError:
        pass

    try:
        return entry.published_parsed
    except AttributeError:
        pass

    return [0, 0, 0, 0, 0, 0, 0, 0, 0]


def _pretty_time(ago):

    if ago < 3600:
        time_length = 0
        time_unit = "New!"
    elif ago < 43200:
        time_length = int(round(ago / 3600))
        time_unit = "hour"
    elif ago < 2419200:
        time_length = int(round(ago / 86400))
        time_unit = "day"
    else:
        time_length = int(round(ago / 2419200))
        time_unit = "month"

    if time_length > 1:
        time_unit += "s"

    return (time_length, time_unit)


# Template functions
def get_entries(url, count=5):
    feed = _get_feed(url)
    return feed.entries[0:count]


def find_link(text, index=0):
    urls = re.findall(r'href="([^"]+)"', text)
    return urls[index]


def get_weather(latlngs):
    data = []
    for lat, lng in latlngs:
        data.append(noa(lat, lng))

    return data


def time_sort(urls, per_feed_count=1):
    """Display the entry with time posted prefixed"""
    entries = []
    time_list = {}
    for url in urls:
        feed = _get_feed(url)

        if len(feed.entries):
            feed_entries = feed.entries[:per_feed_count]
            for entry in feed_entries:
                entry.feed_title = feed.feed.title.split("-")[0]

                pub = _get_date(entry)

                ago = time.mktime(time.localtime()) - time.mktime(pub)
                # unique key
                while ago in time_list:
                    ago += 0.1

                time_list[ago] = True

                entry.time_raw = ago
                entry.time_length, entry.time_unit = _pretty_time(ago)
                entries.append(entry)

    if len(entries):
        return sorted(entries, key=lambda k: k.time_raw)
    else:
        return []


def get_log():
    return log_stream.getvalue()


def find_images(html_string):
    soup = BeautifulSoup(html_string, "html.parser")

    img_src = []
    for img in soup.find_all("img"):
        img_src.append(img.get("src"))

    return img_src


def parse(template, outfile, opts):
    global options
    options = opts
    if options.cache:
        print("Caching requests")
        requests_cache.install_cache("ankh_cache", backend="sqlite")

    full_path = os.path.abspath(template)
    path = os.path.dirname(full_path)

    opts.template_paths.append(path)

    env = Environment(loader=FileSystemLoader(opts.template_paths), autoescape=True)

    env.globals["get_entries"] = get_entries
    env.filters["find_link"] = find_link

    env.globals["time_sort"] = time_sort
    env.globals["images"] = find_images

    env.globals["get_weather"] = get_weather
    env.globals["log"] = get_log

    print("Loading %s" % template)
    template = env.get_template(full_path.replace(path + "/", ""))

    print("Rendering...")

    html = template.render()
    outfile = codecs.open(outfile, "w", "utf-8")
    outfile.write(html)
    outfile.close()
