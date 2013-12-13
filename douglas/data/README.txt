=====
README
======

To compile blog
===============

To render your blog:

    douglas-cmd compile

This will compile your blog to the directory specified by "compiledir" in your
config.py file.


To create an entry
==================

Create a new file in entries/ with any text editor. Use this template:

%%<---------------------------------------------------------
Title of blog entry
#published YYYY-MM-DD HH:MM
#tags tag1::tag2::tag3

<p>
  This is the contents of your blog entry in raw html.
</p>
%%<---------------------------------------------------------
