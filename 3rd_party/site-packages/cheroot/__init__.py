"""High-performance, pure-Python HTTP server used by CherryPy."""

try:
    import pkg_resources
except ImportError:
    pass


try:
    __version__ = pkg_resources.get_distribution('cheroot').version
except Exception:
    __version__ = 'unknown'
