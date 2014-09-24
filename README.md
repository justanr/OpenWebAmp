OpenWebAmp
==========

It really whips the Python's Ass.

OpenWebAmp (OWA) is an attempt to build a sharable web music player based on API first principles.

* API First: By designing OWA's API first, rather than as a traditional website, makes extending it's services simple.
    * RESTful: OWA's API is designed to be RESTful, storing and transfering only data between client and server.
    * Discoverable: Each subresource contained in a response also communicates needed information about location.
    * JSON: Because JSON is easy to work with.
* Sharable: Build and share playlists among other members and tag artists with genres.

###Features

* Stream music files easily through the web
* Build and share playlists of favorite tracks
* Tag artists with every genre imaginable

###Use
Currently, OpenWebAmp is just a service initiated from the command line.

    python manager.py add -d /path/to/music/directory

OpenWebAmp will crawl (recursively) the target directory and process any compatible music file it discovers. Processing consists simply of pulling relevant metadata information out of the file and storing it in a RDBMS.

After that, you can view:

* `host/artist/` for artist listing
* `host/album/` for album listing
* `host/track/` for track listing.

Additionally, each of these endpoints supports an `/<int:id>/` portion that will allow you to view an individual resource.

###Streaming

Each track supports streaming. `host/stream/<str:uuid>/` handles this.

However, currently streaming is handled by Flask sending a file resource instead of passing this off to a HTTP server. This will be removed when development moves beyond initial feature implementation.

###Why?
Undoubtedly, this question will be asked numerous times. The only real answer is: Why not? I've built small APIs for practice before but nothing I've been excited about sharing, but this project is something I do want to share.

There are better options for putting music in the cloud, I'll admit that. However, reinventing the wheel leads to understanding. What do I hope to learn?

* Structuring projects: Especially avoiding things like circular imports and dependencies.
* Developing a deeper understanding of Python, Flask and SQLAlchemy.
* Learning proper RESTful API techniques:
    * Building a stateless member system
    * Finding the right balance of information to communicate with each request
    * Being discoverable and self-documenting
* Writing documentation covering most aspects of the application
* Deploying to various server stacks
* Utilizing git in day-to-day programming
* Testing: when, what, where and how often to test

###Requirements
OpenWebAmp was developed using Python 3.4; however, I believe it should be backwards compatible to 3.0 and with some tinkering to 2.7/6.

I am planning to initially deploy OWA to Nginx and use X-Accel headers to serve media.

The `awesome_slugify` package depends on `regex` which requires the Python development package to be installed.

Other than that, everything else is listed in the REQUIREMENTS file.
