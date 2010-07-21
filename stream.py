import feedparser
import re

def load_feed(url, display):
    feed = feedparser.parse(url)
    s = []
    for entry in feed.entries[0:5]:
        s.append(display(entry))
    return "".join(s)


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

def display_simple(entry, start=False, end=False):
    return  "<li>%s" % entry.content[0].value

display_functions = {
    "simple": display_simple,
}

def main():
    f = open("stream.template")
    template = f.read()
    output = render(template, {})
    print "".join(output)

if __name__ == "__main__":
    main()
