FlaskAmp
========

It really whips the Python's Ass.

FlaskAmp is attempt to build a web based music player.

Use
---

Currently, the only way to add tracks is through the Flask-Script manager script.

    ```python
    python manager.py add -d /path/to/audio/directory/
    ```

That will search the directory for applicable files, open them, parse them and stuff them into the database.

After that, you can use `/album/`, `/artist/`, and `/track/` as well their `<id>` option to view the data.

You can also currently stream audio by navigating to `/stream/<stream_id>/`. For now, the streaming is handled by Flask and whichever WSGI server is handling it.

Obviously, this will need to be changed since an actual web server will handle static files better.

Why?
----
I'm sure I'll be asked this time and time again. There are better options for putting your music library "in the cloud."

The real answer is because I can. I've built small APIs before but nothing I've cared to share.

The other reason being is that there is a bunch of stuff that goes with a project like this:

* Properly laying out modules
* Audio data processing
* Going beyond user authorizations to also handling and securing tokens

Features
--------
Currently, FlaskAmp is just a barebones API. But there's more in the works.

* FlaskAmp was always concieved to be an API based design. There is not native UI to it.
* Streaming -- eventually: it's not really a web based player if there's no streaming.
* Member playlists -- eventually: Why play just single tracks or albums when you can build your own tracklist?
* Tags -- eventually: Allow members to tag artists with their own tags.


Issues
------

* There are no tests! AHHH! But seriously, I need to write some.
* The code's messy and there's a couple of hacks in there (looking at you, TinyTag unicode).
* Streaming, members and playlists aren't implemented.
* Flask-Script is used and Click is installed as well. I'd like to convert to Click instead.


Requirements
------------
FlaskAmp itself was developed using Python 3.4. Currently, there are no immediate plans to test it with other versions. However, there is, no reason this won't happen (I'm more concerned with getting the thing working).

I'm also planning on implementing Streaming with X-Accel headers. To my knowledge, this'll limit FlaskAmp to Nginx.

Beyond that, there is the `requirements` file which lists everything else needed for this build.


