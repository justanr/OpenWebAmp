'''
    
    flaskamp.app.utils.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Utilities for aiding with models.

    :copyright: (c) 2014 Alec Nikolas Reiter
    :license: GNU GPLv3, see LICENSE for more details

'''

def _unique(session, cls, hashfunc, queryfunc, constructor, *args, **kwargs):
    '''Codifies the find or create behavior needed for certain lookups for models.

    :param session: SQLAlchemy session,
    :param cls: Model class being queried or created
    :param hashfunc: Unique hash function
    :param queryfunc: Unique query function
    :param constructor: constructor for the model beign queried or created
    :param args: A collection of positional arguments to send to the hashfunc,
        queryfunc and constructor
    :param dict kwargs: A collection of named arguments to send to the hashfunc.
        queryfunc and constructor

    Source: https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/UniqueObject
    '''

    cache = getattr(session, '_unique_cache', None)
    
    if not cache:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*args, **kwargs))

    if key in cache:
        return cache[key]
    else:
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *args, **kwargs)
            obj = q.first()

            if not obj:
                obj = constructor(*args, **kwargs)
                session.add(obj)

        cache[key] = obj
        return obj
 
class UniqueMixin(object):
    '''Actually implements the unique object recipe for models.
    '''

    @classmethod
    def find_or_create(cls, session, *args, **kwargs):
        '''Simply wraps :func:_unique as a classmethod.
        '''
        return _unique(
            session,
            cls,
            cls.unique_hash,
            cls.unique_func,
            cls,
            *args,
            **kwargs
            )

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        raise NotImplementedError(
            'unique_hash not implemented on '
            'app.utils.models.UniqueMixin'
            )
                

    @classmethod
    def unique_func(cls, *args, **kwargs):
        raise NotImplementedError(
            'unique_func not implemented on'
            'app.utils.models.UniqueMixin'
            )


class ReprMixin(object):
    '''Provides a string representible form for objects.'''

    # Most models will have both an id and name fields
    # This can be overwritten if needed
    __repr_fields__ = ['id', 'name']

    def __repr__(self):
        fields =  {f:getattr(self, f, '<BLANK>') for f in self.__repr_fields__}
        # constructs a dictionary compatible pattern for formatting
        # {{{0}}} becomes {id} for example
        pattern = ['{0}={{{0}}}'.format(f) for f in self.__repr_fields__]
        pattern = ' '.join(pattern)
        pattern = pattern.format(**fields)
        return '<{} {}>'.format(self.__class__.__name__, pattern)
