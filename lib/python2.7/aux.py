#!/usr/bin/python

from log import log

# this is taken from numpy's iotools:
def _is_string_like(obj):
    """
    Check whether obj behaves like a string.
    .
    Using this way of checking for a string-like object is more robust when
    dealing with stuff that can behave like a 'str' but is not strictly an
    instance of it (or a subclass thereof). So it's more generic than using
    isinstance(obj, str)
    """
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True


def check_filehandle(filename, mode):
    '''Make sure a variable is either a filehandle or create one from it.
    .
    This function takes a variable and checks whether it is already a
    filehandle with the desired mode or a string that can be turned into
    a filehandle with that mode. This can be used e.g. to make functions
    agnostic against being supplied a file-type parameter that was gathered
    via argparse (then it's already a filehandle) or as a plain string.
    .
    Parameters
    ----------
    filename : str or filehandle
    mode : str
        The desired mode of the filehandle.
    .
    Returns
    -------
    A valid (open) filehandle with the given mode. Raises an IOError
    otherwise.
    '''
    log.debug(type(filename))
    if (type(filename).__name__ == 'str'):
        try:
            return open(filename, mode)
        except IOError as e:
            message = "can't open '%s': %s"
            raise SystemExit(message % (filename, e))
    elif (type(filename).__name__ == 'file'):
        if (filename.mode != mode):
            message = "mode mismatch: %s != %s"
            raise IOError(message % (filename.mode, mode))
        return filename
    else:
        message = "unknown data type (expected string or filehandle): %s"
        raise SystemExit(message % type(filename))

def filename(name):
    '''Get the filename from either a filehandle or a string.
    .
    This is a convenience function to retrieve the filename as a string
    given either an open filehandle or just a plain str containing the
    name.
    .
    Parameters
    ----------
    name : str or filehandle
    .
    Returns
    -------
    name : str
    '''
    if isinstance(name, file):
        return name.name
    elif _is_string_like(name):
        return name
    else:
        raise TypeError
