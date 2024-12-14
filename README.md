##Ankh
Ankh hooks up jinja2 to feedparser so that you can create your own
simple feed pages. In addition to all the things jinja2 can do Ankh adds
some custom functions and filters.

##Installation

`pip install git+https://github.com/jdcantrell/ankh.git@master#egg=Ankh`

##Functions and filters
`get_entries()` - for generating a list from a url:

```html+django
{% for entry in get_entries('http://goodorobot.net/rss') %}
  <li>
    <a href="{{entry.link}}">{{entry.title}}</a>
    <a class="comment" href="{{entry.comments}}">
      <i class="icon-comment"></i>
    </a>
  </li>
{% endfor %}
```

The entry is a feedparser object so anything available to feedparser is
available here.

`entry.description|find_link(1)` - for finding a url that is in embedded
within some text. It takes in a parameter for which link to return
(0-indexed)

`time_sort()` - Takes a list of urls, fetches the newest entry from each
url, and then sorts them all together from most recent to oldest.

```html+django
{% for entry in time_sort([
  'http://magicalgametime.com/rss',
  'http://simoncottee.blogspot.com/feeds/posts/default',
  'http://oktotally.tumblr.com/rss']) %}

 {{entry.time_length}} {{entry.time_unit}} {{entry.title}}

{% endfor %}
```

Entries for `time_sort()` are also feedparser objects, it
has four additional attributes:

- entry.time_length - an integer
- entry.time_unit - either hour(s), day(s) or month(s) or New!
- entry.time_raw - the raw time value used to sort
- entry.feed_title - the title of the feed for the current entry

`get_weather()` - takes a list of latitudes, longitude pairs and will
return an object for reading the weather (uses NOAA dwml).

```html+django
{% for weather in get_weather([
  (37.91583, -122.03583),
  (45.52, -122.6819),
  (43.6167, -116.2),
  (38.7453, -94.8292)
]) %}
  <li title="{{ weather.condition() }}">
    {{ weather.temp() }}&deg; in {{ weather.forecast_location() }}
  </li>
{% endfor %}
```

##Running

Suggested use: `ankh my.template.html index.html`

Other flags:

- `-c` - read and/or write cache files for each feed parsed (useful when
  developing a template)
- `--cache-path path` - specify the cache path, defaults to `.ankh_cahe`
- `-v` - verbose, more details about what is going on

Also works great in a cron :)

##Development

1. git clone
2. poetry install
3. poetry run ankh -v test.template.html.j2
