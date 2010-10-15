'''Ankh - will parse a template with {{http://somewhere/rss/feed|fn}} tags
fetching the feeds and running the function on each item in the feed'''
from optparse import OptionParser
import feedparser
import re
import codecs

import ankh_displays 

def load_feed(url, display, count, options):
    '''Uses feedparser to fetch feeds and parse through the correct display
    function'''
    if options.verbose:
        print "Parsing %s(%d entries)..." % (url, count)

    feed = feedparser.parse(url)
    output = ['']
    for entry in feed.entries[0:count]:
        output.append(display(entry))
    output.append('')
    return u'\n\t\t\t'.join(output)


def render(template, options):
    '''based off http://effbot.org/zone/django-simple-template.htm
    parses jinja2 like template tags of the form {{url|fn|count}}'''
    nxt = iter(re.split("({{|}})", template)).next
    data = []
    try:
        token = nxt()
        while 1:
            if token == "{{":  # variable
                data.append(variable(nxt(), options))
                if nxt() != "}}":
                    raise SyntaxError("Missing variable terminator")
            else:
                data.append(token)  # literal
            token = nxt()
    except StopIteration:
        pass

    return data


def variable(var, options):
    '''This will parse a text between {{ and }} in a template'''
    url = var.strip()
    function = "simple"
    count = 5

    if "|" in var:
        url, function = var.split("|", 1)
        if "|" in function:
            function, count = function.split("|", 1)
            count = int(count.strip())
    return load_feed(url, ankh_displays.DISPLAY_FUNCTIONS[function], \
            count, options)
#End shameless code cut 'n paste


def main():
    parser = OptionParser()
    parser.add_option("-t", "--template", dest="template", \
        help="Template file to load. Defaults to ankh.template", \
        default="ankh.template")
    parser.add_option("-o", "--outfile", dest="outfile", \
        help="File to save the parsed template and feeds to. Defaults to \
        ankh.html", default="ankh.html")
    parser.add_option("-v", "--verbose", dest="verbose", \
        help="Be verbose about what is going on", action="store_true",
        default=False)

    options = parser.parse_args()[0]

    template_file = codecs.open(options.template, "r", "utf-8")
    template = template_file.read()
    template_file.close()
    output = render(template, options)
    outfile = codecs.open(options.outfile, "w", "utf-8")
    outfile.write(u''.join(output))

if __name__ == "__main__":
    main()
