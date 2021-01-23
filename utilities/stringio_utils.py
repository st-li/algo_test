from contextlib import contextmanager


@contextmanager
def buildStringIO(strData=None):
    from io import StringIO
    try:
        fi = StringIO(strData) if strData else StringIO()
        yield fi
    finally:
        fi.close()