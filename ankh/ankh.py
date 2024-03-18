"""Ankh - will parse a template with {{http://somewhere/rss/feed|fn}} tags
fetching the feeds and running the function on each item in the feed"""
import os
import codecs
import time
import re
import logging
import io
import pytz
import functools
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup, escape

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


@functools.cache
def _load_url(url):
    global options
    if options.verbose:
        print("Fetching: %s" % url)
    try:
        headers = {
            "User-Agent": "idk-testing",
            "If-Modified-Since": "Wed, 21 Oct 2015 07:28:00 GMT",
        }
        r = requests.get(url, timeout=120, headers=headers)
        return r.text
    except requests.exceptions.RequestException as e:
        logger.error("Could not fetch %s" % url)
        logger.error("Exception was raised: %r" % e)

    return ""


def _get_feed(url):
    data = None

    if data is None:
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

    return [1970, 1, 1, 0, 0, 0, 0, 1, 0]


def _timestamp(date):
    try:
        return time.mktime(date)
    except:
        return 0


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
    ss = sorted(
        feed.entries, key=lambda entry: _timestamp(_get_date(entry)), reverse=True
    )[0:count]

    return ss


def get_date():
    return datetime.now(pytz.timezone("US/Pacific"))


def find_link(text, index=0):
    urls = re.findall(r'href="([^"]+)"', text)
    return urls[index]


def ignore_entities(text):
    parts = re.split(r"(&#?[0-9A-Za-z]+;)", text)
    escaped = []
    for part in parts:
        if "&" in part:
            escaped.append(part)
        else:
            escaped.append(escape(part))

    return Markup("".join(escaped))


def get_weather(latlngs):
    data = []
    for lat, lng in latlngs:
        data.append(noa(lat, lng))

    return data


def get_status(url):
    headers = {"User-Agent": "linux:net.goodrobot.ankh:v0.0.1 (by /u/jdcantrell)"}
    try:
        r = requests.get(url, timeout=5, headers=headers)
    except:
        return "xxx"

    return r.status_code


def time_sort(urls, per_feed_count=1):
    """Display the entry with time posted prefixed"""
    entries = []
    time_list = {}
    for url in urls:
        feed = _get_feed(url)

        if len(feed.entries):
            # sort by date desc - not all feeds come in chronological order
            feed_entries = sorted(
                feed.entries,
                key=lambda entry: _timestamp(_get_date(entry)),
                reverse=True,
            )[0:per_feed_count]

            for entry in feed_entries:
                if "title" in feed.feed:
                    entry.feed_title = feed.feed.title.split("-")[0]
                else:
                    entry.feed_title = ""

                pub = _get_date(entry)

                ago = time.mktime(time.localtime()) - time.mktime(pub)
                # unique key
                while ago in time_list:
                    ago += 0.1

                time_list[ago] = True

                entry.time_raw = ago
                entry.time_length, entry.time_unit = _pretty_time(ago)
                entries.append(entry)
        else:
            print(" ^^^ No entries found")

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
        requests_cache.install_cache(
            "ankh_cache",
            backend="sqlite",
            expire_after=timedelta(days=1),
            always_revalidate=True,
        )

    full_path = os.path.abspath(template)
    path = os.path.dirname(full_path)

    opts.template_paths.append(path)

    env = Environment(loader=FileSystemLoader(opts.template_paths), autoescape=True)

    env.globals["get_entries"] = get_entries
    env.filters["find_link"] = find_link
    env.filters["ignore_entities"] = ignore_entities

    env.globals["time_sort"] = time_sort
    env.globals["images"] = find_images

    env.globals["get_weather"] = get_weather
    env.globals["log"] = get_log
    env.globals["get_date"] = get_date

    env.globals["get_status"] = get_status

    print("Loading %s" % template)
    template = env.get_template(full_path.replace(path + "/", ""))

    print("Rendering...")

    pacific_time = datetime.now(pytz.timezone("US/Pacific"))
    html = template.render(timestamp=time.time(), date=pacific_time)
    outfile = codecs.open(outfile, "w", "utf-8")
    outfile.write(html)
    outfile.close()
