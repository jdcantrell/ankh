import time

def display_simple(entry):
    if entry.has_key('content'):
        return  u'<li>%s' % entry.content[0].value
    return u'<li>%s' % entry.title

def display_link(entry):
    return u'<li><a href="%s">%s</a>' % (entry.link, entry.title)

def display_vimeo(entry):
    return u'<li><object width="310" height="232"><param name="allowfullscreen" \
        value="true" /><param name="allowscriptaccess" value="always" />\
        <param name="movie" value="%s&amp;server=vimeo.com&amp;show_title=1\
        &amp;show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1"\
        /><embed src="%s&amp;server=vimeo.com&amp;show_title=1&amp;\
        show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1"\
        type="application/x-shockwave-flash" allowfullscreen="true"\
        allowscriptaccess="always" width="310" height="232"></embed>\
        </object>' % (entry.enclosures[0].href, entry.enclosures[0].href);

def display_delicious(entry):
    if entry.has_key("summary"):
        return u'<li><a href="%s">%s</a> - %s' % (entry.link, entry.title, \
    entry.summary)
    return u'<li><a href="%s">%s</a>' % (entry.link, entry.title)

def display_identica(entry):
        return  u'<li>%s <span class="entry-meta">%s</span>' % \
            (entry.content[0].value, time.strftime("%a, %B %d, %Y", \
                                                        entry.date_parsed))


#Add in custom displays below, be sure to add them to the display_functions
#list as well!

display_functions = {
    "simple": display_simple,
    "link": display_link,
    "vimeo": display_vimeo,
    "delicious": display_delicious,
    "identica": display_identica,
}
