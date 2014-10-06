from flask.ext.marshmallow import Marshmallow

from .utils.schema import Polymorphic, Length, counted

# lowest common fields for serialized models
common = ('slug', 'name')

ma = Marshmallow()

class BaseSchema(ma.Serializer):
    class Meta:
        additional = common

class TracklistSchema(BaseSchema): 
    tracks = ma.Nested(
        'TrackSchema',
        exclude=('tracklists',),
        many=True
        )
    owner = Polymorphic(
        mapping={
            'Member' : 'MemberSchema',
            'Artist' : 'ArtistSchema'
            },
        default_schema='BaseSchema',
        only=(common+('links',))
        )
    length = Length()
    total_tracks = ma.Integer()
    links = ma.Hyperlinks({
        'self' : ma.URL('tracklist', slug='<slug>', _external=True),
        'collection' : ma.URL('tracklists', _external=True)
        })

class ArtistSchema(BaseSchema):
    albums = ma.Nested('TracklistSchema', only=common+('links',), many=True)
    links = ma.Hyperlinks({
        'self' : ma.URL('artist', slug='<slug>', _external=True),
        'collection' : ma.URL('artists', _external=True)
        })
    tags = ma.Function(
        counted(
            target='tags',
            schema='TagSchema',
            only=('id', 'name', 'links')
            )
        )


class MemberSchema(BaseSchema):
    bio = ma.String()    
    playlists = ma.Nested('TracklistSchema', only=common+('links',), many=True)
    links = ma.Hyperlinks({
        'self' : ma.URL('member', slug='<slug>', _external=True),
        'collection' : ma.URL('members', _external=True)
        })
    tags = ma.Function(
        counted(
            target='tags', 
            schema='TagSchema',
            only=('id', 'name', 'links')
            )
        )

class TrackSchema(BaseSchema):
    length = Length()
    artist = ma.Nested('ArtistSchema', only=common+('links',))
    tracklists = ma.Nested(
        'TracklistSchema',
        many=True,
        exclude=('tracks', 'length')
        )
    links = ma.Hyperlinks({
        'stream' : ma.URL('stream.stream', stream_id='<stream>', _external=True),
        'self' : ma.URL('track', slug='<slug>', _external=True),
        'collection' : ma.URL('tracks', _external=True)
        })


class TagSchema(BaseSchema):
    links = ma.Hyperlinks({
        'self' : ma.URL('tag', slug='<slug>', _external=True),
        'collection' : ma.URL('tags', _external=True)
        })
    artists = ma.Function(
        counted(
            target='artists',
            schema='ArtistSchema',
            only=('id', 'name', 'links')
            )
        )
    total = ma.Integer()
