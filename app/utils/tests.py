'''
    
    Unit Test Utilities
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Alec Nikolas Reiter
    :license: MIT, see LICENSE for more details

'''

def GenericCls(clsname, clsattrs=None):
    '''Returns a generic, dynamically created class with the given name
    and class attributes preset. It also creates a dunder init method 
    that can set instance keyword attributes.
    '''

    attrs={}

    if clsattrs:
        attrs.update(clsattrs)

    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    attrs['__init__'] = __init__
    
    return type(clsname, (object,), attrs)

def GenericObj(clsname, clsattrs=None, **instattrs):
    '''Returns an object from a dynamically created class with the given
    name and attributes preset.

    Useful if you need a generic class but only a for a singluar object.
    '''

    return GenericCls(clsname, clsattrs)(**instattrs)
