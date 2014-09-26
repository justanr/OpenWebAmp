from flask.ext.marshmallow import Marshmallow

from .utils.schema import Polymorphic, Length

# lowest common fields for serialized models
common = ('id', 'name')

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

    links = ma.Hyperlinks({
        'self' : ma.URL('tracklist', id='<id>', _external=True),
        'collection' : ma.URL('tracklists', _external=True)
        })

class ArtistSchema(BaseSchema):
    albums = ma.Nested('TracklistSchema', only=common+('links',), many=True)
    links = ma.Hyperlinks({
        'self' : ma.URL('artist', id='<id>', _external=True),
        'collection' : ma.URL('artists', _external=True)
        })

    top_tags = ma.Method('counted_tags')

    def counted_tags(self, obj):
        result = []

        for tag, count in obj.top_tags:
            data = TagSchema(tag, exclude=('top_artists',)).data
            data['count'] = count
            result.append(data)

        return result

class MemberSchema(BaseSchema):
    bio = ma.String()
    playlists = ma.Nested('TracklistSchema', only=common+('links',), many=True)
    links = ma.Hyperlinks({
        'self' : ma.URL('member', id='<id>', _external=True),
        'collection' : ma.URL('members', _external=True)
        })

    top_tags = ma.Method('counted_tags')

    def counted_tags(self, obj):
        result = []

        for tag, count in obj.top_tags:
            data = TagSchema(tag, exclude=('top_artists',)).data
            data['count'] = count
            result.append(data)

        return result



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
        'self' : ma.URL('track', id='<id>', _external=True),
        'collection' : ma.URL('tracks', _external=True)

        })

class TagSchema(BaseSchema):
    links = ma.Hyperlinks({
        'self' : ma.URL('tag', id='<id>', _external=True),
        'collection' : ma.URL('tags', _external=True)
        })
    top_artists = ma.Method('counted_artists')

    def counted_artists(self, obj):
        result = []

        for art, count in obj.top_artists:
            data = ArtistSchema(art, only=common+('links',)).data
            data['count'] = count
            result.append(data)

        return result
