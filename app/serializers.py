from flask.ext.marshmallow import Marshmallow

# Serializers

ma = Marshmallow()

class ArtistSerializer(ma.Serializer):
    albums = ma.Nested('AlbumSerializer', exclude=('artist',), many=True)

    links = ma.Hyperlinks({
        'self' : ma.URL('artist', id='<id>'),
        'collection' : ma.URL('artists')
        })

    class Meta:
        fields = ('id', 'name', 'albums', 'links')

class AlbumSerializer(ma.Serializer):
    artist = ma.Nested('ArtistSerializer', exclude=('albums',))
    tracks = ma.Nested('TrackSerializer', exclude=('album', 'artist'), many=True)

    links = ma.Hyperlinks({
        'self' : ma.URL('album', id='<id>'),
        'collection' : ma.URL('albums')
    })

    class Meta:
        fields = ('id', 'artist', 'name', 'tracks', 'links')

class TrackSerializer(ma.Serializer):
    artist = ma.Nested('ArtistSerializer', only=('name', 'links'))
    album = ma.Nested('AlbumSerializer', only=('name', 'links'))
    length = ma.Method('convert_time')

    links = ma.Hyperlinks({
        'self' : ma.URL('track', id='<id>'),
        'collection' : ma.URL('tracks')
    })

    def convert_time(self, track):
        mins = track.length//60
        seconds = track.length - (mins * 60)
        return "{!s:0>2}:{!s:0>2}".format(mins, seconds)


    class Meta:
        fields = (
            'id', 'artist', 'album' ,'name', 
            'position', 'length', 
            'links', 'stream'
            )

