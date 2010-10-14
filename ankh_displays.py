import time


def display_simple(entry):
    if 'content' in entry:
        return  u'<li>%s' % entry.content[0].value
    return u'<li>%s' % entry.title


def display_link(entry):
    if entry.title == u'':
        entry.title = u'Untitled'
    return u'<li><div class="story"><a href="%s">%s</a></div>' % (entry.link, entry.title)


def display_vimeo(entry):
    return (u'<li><object width="310" height="232">'
            u'<param name="allowfullscreen" value="true">'
            u'<param name="allowscriptaccess" value="always">'
            u'<param name="movie" value="%s&amp;server=vimeo.com&amp;'
            u'show_title=1&amp;show_byline=1&amp;show_portrait=0'
            u'&amp;color=&amp;fullscreen=1">'
            u'<embed src="%s&amp;server=vimeo.com&amp;show_title=1&amp;'
            u'show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1"'
            u'type="application/x-shockwave-flash" allowfullscreen="true"'
            u'allowscriptaccess="always" width="310" height="232">'
            u'</object>') % (entry.enclosures[0].href, \
                entry.enclosures[0].href)


def display_delicious(entry):
    if 'summary' in entry:
        return u'<li><a href="%s">%s</a> - %s' % (entry.link, entry.title, \
    entry.summary)
    return u'<li><a href="%s">%s</a>' % (entry.link, entry.title)


def display_identica(entry):
    return  u'<li>%s <div class="entry-meta">%s</div>' % (
        entry.content[0].value, time.strftime("at %I:%M %P on %A, %B %d, %Y",
        entry.date_parsed))


def display_hn(entry):
    if entry.title == u'':
        entry.title = u'Untitled'
    return u'<li><div class="story"><a href="%s">%s</a><div class="details"> \
        <a class="comment-link" href="%s">Comments</a></div></div>' % \
        (entry.link, entry.title, entry.comments)
#Add in custom displays below, be sure to add them to the display_functions
#list as well!
display_functions = {
    "simple": display_simple,
    "link": display_link,
    "vimeo": display_vimeo,
    "delicious": display_delicious,
    "identica": display_identica,
    "hn": display_hn,
}
