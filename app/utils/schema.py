"""

    flaskamp.utils.schema
    ~~~~~~~~~~~~~~~~~~~~~

    Utilities for object serialization schemas.

    This module only contains custom fields, helpers and if needed 
    customizations to base schema classes.

    :copyright: (c) 2014 Alec Nikolas Reiter
    :license: MIT, see LICENSE for more details

"""

from marshmallow import fields
from marshmallow.class_registry import get_class as get_schema
from marshmallow.compat import basestring

# units of time in seconds
_time_units = [
    3600,   # one hour
    60,     # one minute
    1,      # one second
    ]

def _convert_seconds_to_time(seconds, units=_time_units):
    '''Converts a time given in seconds to a human readable time.
    This is an internal helper for the :class:`Length` field.

    Examples::
        _convert_seconds_to_time(42)   -> 00:42
        _convert_seconds_to_time(244)  -> 04:04
        _convert_seconds_to_time(6036) -> 01:40:36

    :param int seconds: Length of object in seconds
    :param list units: List of time units in seconds
    '''

    result = []
    
    for unit in units:
        part, seconds = seconds//unit, seconds%unit
        if part:
            result.append('{:0>2}'.format(part))
    
    if len(result) == 1:
        results.insert(0, '00')

    return ':'.join(parts)

class Polymorphic(fields.Field):
    '''Allows nesting of several potential schemas inside of a single field.
    This field should be used with `marshmallow.fields.List` if a collection of
    polymorphic objects is given.

    Examples::

        tracklist = Polymorphic(
            mapping={
                'Album':'AlbumSchema',
                'Playlist':'PlaylistSchema'
                },
            default_schema='TracklistSchema'
            )

        # exactly the same as above
        tracklist = Polymorphic(
            mapping={
                'Album':AlbumSchema,
                'Playlist':PlaylistSchema
                },
            default_schema=TracklistSchema
            )
    

    :keyword dict mapping: A dictionary mapping of class names to schemas.
        Schemas may be given as classes or strings.
    :keyword Schema default_schema: Used as a fallback when an object does not
        match in the object-schema mapping.
    :keyword only: A tuple or string of the field(s) to marshal. If ``None``
        all fields will be marshalled. If a single field name (string) is given
        only a single value will be returned as output instead of a dictionary.
        This parameter takes precedence over ``exclude``
    :keyword dict kwargs: A collection of keyword arguments to pass to the
        parent Field class.

    Modified from example by `Steven Loria <https://github.com/sloria>`
    '''

    def __init__(self, mapping, default_schema, only=None, exclude=None, **kwargs):
        self.mapping = mapping
        self.default_schema = default_schema
        self.only = only
        self.exclude = exclude
        super().__init__(**kwargs)

    def output(self, key, obj):
        nested_obj = self.get_value(key, obj)
        obj_name = nested_obj.__class__.__name__
        schema = self.mapping.get(obj_name, self.default_schema)

        # convert from string to schema class if needed
        if isinstance(schema, basestring):
            schema = get_schema(schema)

        serializer = schema(nested_obj, only=self.only, exclude=self.exclude)

        return serializer.data

class Length(fields.Field):
    '''Wrapper around _convert_seconds_to_time for use with Marshmallow schemas.
    '''

    def format(self, value):
        return _convert_seconds_to_time(value)
