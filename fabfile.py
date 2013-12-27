from __future__ import with_statement
from fabric.api import local, run, cd
from fabric.decorators import hosts
from fabric.colors import green, blue, red

code_dir = "/srv/http/goodrobot"
stream_dir = "/home/jd/Projects/ankh"
  
  

def build():
  local("mkdir -p ../goodrobot.net/_site/stream/")
  local("python ankh.py -t goodrobot.template.html -o ../goodrobot.net/_site/stream/index.html -v")

@hosts('jd@goodrobot.net')
def deploy():
  #re-gen the stream page on deploy
  with cd(stream_dir):
    print(blue("Updating codebase..."))
    output = run("git pull")
    if output.find("Already up-to-date") != -1:
      print(red("No changes found to deploy"))
    else:
      _regen()

@hosts('jd@goodrobot.net')
def regen():
  _regen()

def _regen():
  with cd(stream_dir):
    print(blue("Generating page..."))
    run("mkdir -p %s/stream" % code_dir)
    run("python ankh.py -t goodrobot.template.html -o %s/stream/index.html -v" % code_dir)
    print(green("Page generated at http://goodrobot.net/stream"))


