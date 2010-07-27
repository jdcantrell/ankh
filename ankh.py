from optparse import OptionParser
import feedparser
import re
import codecs


from ankh_displays import *

def load_feed(url, display, count):
    print "Parsing feed at %s..." % url
    feed = feedparser.parse(url)
    s = []
    for entry in feed.entries[0:count]:
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
    count = 5
    if "|" in var:
        url, function = var.split("|", 1)
        if "|" in function:
            function, count = function.split("|",1)
    
    return load_feed(url, display_functions[function], count)
#End shameless code cut 'n paste



def main():
    parser = OptionParser()
    parser.add_option("-t","--template", dest="template", help="Template \
        file to load. Defaults to \"ankh.template\"", \
        default = "ankh.template")
    parser.add_option("-o","--outfile", dest="outfile", help="File to save \
        the parsed template and feeds to. Defaults to \"ankh.html\"", \
        default="ankh.html")

    options, args = parser.parse_args()

    template_file = codecs.open(options.template, "r", "utf-8")
    template = template_file.read()
    template_file.close()
    output = render(template, {})
    outfile = codecs.open(options.outfile,"w","utf-8")
    outfile.write(u''.join(output))


if __name__ == "__main__":
    main()
