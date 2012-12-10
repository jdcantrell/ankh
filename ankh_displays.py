'''These are simple functions that parse a single entry in a feed and 
return the html that should be displayed'''
import feedparser
import time
import re
import htmlentities
import pickle

def get_feed(url, options):
  if options.cache:
    clean_url = url.replace("http://","").replace("/", "_");
    try:
      with open('./.ankh_cache/%s.pickle' % clean_url) as file:
        feed = pickle.load(file)
    except IOError as e:
      feed = feedparser.parse(url)

      #TODO: be more robust about broken feeds
      if 'version' in feed:
        with open('./.ankh_cache/%s.pickle' % clean_url, 'w') as file:
          pickle.dump(feed, file)
  else:
    feed = feedparser.parse(url)
  return feed

def parse_feed(fn):
  '''A decorator for displays that only need a single parsed item from 
  feedparser'''
  def new(url, count, options):
    '''Uses feedparser to fetch feeds and parse through the correct display
    function'''
    if options.verbose:
        print "Parsing %s(%d entries)..." % (url, count)

    feed = get_feed(url, options)

    output = ['']
    for entry in feed.entries[0:count]:
        #Call passed in function and append the output
        output.append(fn(entry, feed))
    output.append('')
    return u'\n\t\t\t'.join(output)
  return new

@parse_feed
def display_simple(entry, feed):
    '''Display the title of an entry'''
    if 'content' in entry:
        return  u'<li>%s' % entry.content[0].value
    return u'<li>%s' % htmlentities.encode(entry.title)


@parse_feed
def display_link(entry, feed):
    '''Display the title wrapped in a link'''
    if entry.title == u'':
        entry.title = u'Untitled'
    return u'<li><a href="%s">%s</a>' % \
            (entry.link, htmlentities.encode(entry.title))


@parse_feed
def display_vimeo(entry, feed):
    '''Display the flash object for a vimeo feed entry'''
    return (u'<li><object width="350" height="232">'
            u'<param name="allowfullscreen" value="true">'
            u'<param name="allowscriptaccess" value="always">'
            u'<param name="movie" value="%s&amp;server=vimeo.com&amp;'
            u'show_title=1&amp;show_byline=1&amp;show_portrait=0'
            u'&amp;color=&amp;fullscreen=1">'
            u'<embed src="%s&amp;server=vimeo.com&amp;show_title=1&amp;'
            u'show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1"'
            u'type="application/x-shockwave-flash" allowfullscreen="true"'
            u'allowscriptaccess="always" width="350" height="232">'
            u'</object>') % (entry.enclosures[0].href, \
                entry.enclosures[0].href)

def display_show_ago(urls, count, options):
    urls = re.sub(r'\s','', urls)
    urls = urls.split(',')
    '''Display the entry with time posted prefixed'''
    order = []
    items = {}
    for url in urls:
      if options.verbose:
          print "Parsing %s" % url 
      feed = get_feed(url, options)
      if len(feed.entries):
        entry = feed.entries[0]


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
        while items.has_key(ago):
          ago += .1

        if ago < 3600:
          ago_str = u'!!'
        elif ago < 43200:
          ago_str = u'%dh' % round(ago / 3600)
        elif ago < 2419200:
          ago_str = '%dd' % round(ago / 86400)
        else:
          ago_str = '%dm' % round(ago / 2419200)

        if entry.title == u'':
            entry.title = u'Untitled'

        html = u'<li><span class="time-ago">%s</span> <span class="feed-title">%s -</span>  <a href="%s">%s</a>' % \
                (ago_str, feed.feed.title.split('-')[0], entry.link, htmlentities.encode(entry.title))

        order.append(ago)
        items[ago] = html
      html = '<ul class="link-list">'
    if len(order):
      order.sort()
      for i in order:
        html += items[i]
      html += '</ul>'
      return html
    else:
      return '<ul>Oh no, Captain Jack! We\'ve lost the interweb</ul>'


@parse_feed
def display_delicious(entry, feed):
    '''Display the link and description from a delicious feed'''
    if 'summary' in entry:
        return u'<li><a href="%s">%s</a> - %s' % (entry.link, htmlentities.encode(entry.title), \
    entry.summary)
    return u'<li><a href="%s">%s</a>' % (entry.link, htmlentities.encode(entry.title))


@parse_feed
def display_identica(entry, feed):
    '''Display a identica dent with time'''
    return  u'<li>%s <div class="entry-meta">%s</div>' % (
        entry.content[0].value, time.strftime("at %I:%M %P on %A, %B %d, %Y",
        entry.date_parsed))

@parse_feed
def display_twitter(entry, feed):
    '''Display a twitter dent with time'''
    return  u'<li>%s <div class="twitter-meta">%s</div>' % (
        re.sub(r'^[\w\d]*: ', '', entry.content[0].value), time.strftime("at %I:%M %P on %A, %B %d, %Y",
        entry.date_parsed))

@parse_feed
def display_hn(entry, feed):
    '''Like display_link, but also add in a link to comments'''
    if entry.title == u'':
        entry.title = u'Untitled'
    return u'<li><a href="%s">%s</a><div class="details"> \
        <a class="comment-link" href="%s">Comments</a></div>' % \
        (entry.link, htmlentities.encode(entry.title), entry.comments)

@parse_feed
def display_pinboard(entry, feed):
    #if title does not have [toread] in it
    if entry.title[0:8] != u'[toread]':
        if 'description' in entry:
            return u'<li><a href="%s">%s</a> - %s' % \
                (entry.link, htmlentities.encode(entry.title), entry.description)
        else:
            return u'<li><a href="%s">%s</a>' % (entry.link, htmlentities.encode(entry.title))
    return u''
#display title with link, followed by description if set


#Add in custom displays below, be sure to add them to the display_functions
#list as well!
DISPLAY_FUNCTIONS = {
    "simple": display_simple,
    "link": display_link,
    "vimeo": display_vimeo,
    "delicious": display_delicious,
    "pinboard": display_pinboard,
    "identica": display_identica,
    "twitter": display_twitter,
    "hn": display_hn,
    "show_ago": display_show_ago,
}
