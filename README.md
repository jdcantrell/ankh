Ankh hooks up jinja2 to feedparser so that you can create your own
simple feed pages. In addition to all the things jinja2 can do Ankh adds
three custom filters:

One for generating an iterator from a url:
`{% for entry in 'http://goodorobot.net/rss'|feed %} {{ entry.title }} {% endfor %}`
The entry is a feedparser object so anything available to feedparser is
available here.

Another for takine a list of urls and sorting them all by their most
recent entry:
```
{% for entry in [
  'http://magicalgametime.com/rss',
  'http://simoncottee.blogspot.com/feeds/posts/default',
  'http://oktotally.tumblr.com/rss']|time_sort %}

 {{entry.time_length}} {{entry.time_unit}} {{entry.title}}

{% endfor %}
```
Again entry is a feedparser object, it has four additional attributes:
* entry.time_length - an integer
* entry.time_unit - either hour(s), day(s) or month(s) or New!
* entry.time_raw - the raw time value used to sort
* entry.feed_title - the title of the feed for the current entry

And lastly:
`{{ entry.description|find_link }}` which will look for text that
matches `href="somewhere.net"`. You can pass a number that will return
the nth match, otherwise it returns the first match which is equivalent
to `find_link(0)`.


Things you might need to run this:
* Python
* A Computer
* python-feedparser - http://www.feedparser.org
* Jinja2 - http://jinja.pocoo.org

Suggested use: python ankh.py -t ankh.template -o ankh.html

Also works great in a cron :)
