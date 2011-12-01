from __future__ import with_statement
from fabric.api import local, run, cd
from fabric.decorators import hosts
from fabric.colors import blue, green

def build():
  local("mkdir -p ../goodrobot.net/_site/stream/")
  local("python ankh.py -t goodrobot.template.html -o ../goodrobot.net/_site/stream/index.html -v")

@hosts('jdcantrell@goodrobot.net')
def deploy():
  code_dir = "~/goodrobot.net"
  stream_dir = "~/ankh"
  
  #re-gen the stream page on deploy
  with cd(stream_dir):
    print(blue("Updating ankh and regenerating..."))
    run("git pull")
    run("mkdir -p %s/_site/stream" % code_dir)
    run("python ankh.py -t goodrobot.template.html -o %s/_site/stream/index.html -v" % code_dir)
  print(green("Site has been successfully deployed: http://goodrobot.net"))
