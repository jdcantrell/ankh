import feedparser
import re
import codecs

def load_feed(url, display):
    print "Parsing feed at %s..." % url
    feed = feedparser.parse(url)
    s = []
    for entry in feed.entries[0:5]:
        s.append(display(entry))
    return u''.join(s)


#django simple template - based off http://effbot.org/zone/django-simple-template.htm
def render(template, context):
    next = iter(re.split("({{|}})", template)).next
    data = []
    try:
        token = next()
        while 1:
            if token == "{{": #variable
                data.append(variable(next(), context))
                if next() != "}}":
                    raise SyntaxError("Missing variable terminator")
            else:
                data.append(token) #literal
            token = next()
    except StopIteration:
        pass
    return data

def variable(var, context):
    #print "Found %s" % var
    url = var.strip()
    function = "simple"
    if "|" in var:
        url, function = var.split("|", 1)
    
    return load_feed(url,display_functions[function])
#End shameless code cut 'n paste

def display_simple(entry):
    if entry.has_key('content'):
        return  u'<li>%s' % entry.content[0].value
    return u'<li>%s' % entry.title

def display_link(entry):
    return u'<li><a href="%s">%s</a>' % (entry.link,entry.title)

def display_vimeo(entry):
    return u'<object width="350" height="262"><param name="allowfullscreen" \
        value="true" /><param name="allowscriptaccess" value="always" />\
        <param name="movie" value="%s&amp;server=vimeo.com&amp;show_title=1\
        &amp;show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1"\
        /><embed src="%s&amp;server=vimeo.com&amp;show_title=1&amp;\
        show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1"\
        type="application/x-shockwave-flash" allowfullscreen="true"\
        allowscriptaccess="always" width="350" height="262"></embed>\
        </object>' % (entry.enclosures[0].href, entry.enclosures[0].href);

display_functions = {
    "simple": display_simple,
    "link": display_link,
    "vimeo": display_vimeo,
}


def main():
    f = codecs.open("stream.template", "r", "utf-8")
    template = f.read()
    f.close()
    output = render(template, {})
    outfile = codecs.open("stream.html","w","utf-8")
    outfile.write(u''.join(output))


if __name__ == "__main__":
    main()
