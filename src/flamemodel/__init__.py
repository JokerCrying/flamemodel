from __future__ import annotations

from .main import FlameModel

# models
from .models import (
    String, Hash, Set,
    Geo, HyperLogLog,
    List, ZSet, BitMap,
    Stream
)
from .models.fields import fields

__version__ = "0.0.1"
__author__ = "surp1us"
__description__ = ""

__all__ = (
    'FlameModel',
    'Stream',
    'Set',
    'String',
    'HyperLogLog',
    'Hash',
    'List',
    'ZSet',
    'BitMap',
    'Geo',
    'fields'
)
