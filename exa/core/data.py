# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Frame
#########################
The :class:`~exa.core.frame.Frame` object looks and behaves just like a
:class:`~pandas.DataFrame`.

Data consists of dimensions and features. Dimensions describe the extent of the
space occupied by the data. Features describe the individual values at given
points in the space of the data. Dimensions can be defined as discrete arrays
or by parameterized functions. A common example is weather data. Dimensions of
weather data may be longitude, latitude, and time. Examples features of weather
data may be temperature and precipitation.

The number of dimensions determine the dimensionality of the data (in the weather
example there are three dimensions, two spatial and one temporal). There can be
an arbitrary number of features. In computational work it can be useful to perform
'record keeping' which is accomplished by maintaining a unique identifier (index)
with every point in the space of the data.

Default data objects are built on top `pandas`_. The :class:`~pandas.DataFrame`
is extended to represent a multidimensional object. TODO

.. _pandas: http://pandas.pydata.org/
"""
import six
import pandas as pd
import numpy as np
from .base import ABCBase, ABCBaseMeta


class _Frame(ABCBaseMeta):
    """Additional typed attributes."""
    dimensions = (list, tuple)
    units = dict


class Frame(six.with_metaclass(_Frame, pd.DataFrame, ABCBase)):
    """
    A thin wrapper around :class:`~pandas.DataFrame` enabling support for
    multi-featured, explicitly multi-dimensional data.
    """
    # Pandas has its own (partial) system of metadata propagation
    _metadata = ["name", "units", "dimensions", "uid", "meta"]

    @property
    def _constructor(self):
        """
        Used by pandas finalization mechanism
        """
        return Frame

    def copy(self, *args, **kwargs):
        """Return a copy of this object."""
        cp = super(FrameData, self).copy(*args, **kwargs).__finalize__(self)
        return self._constructor(cp)

    def __init__(self, *args, **kwargs):
        """
        Args:
            uid (UUID): Object unique id
            meta (dict): Dictionary containing metadata
            dimensions (list): List of column names representing dimensions
            units (dict): Dictionary of column name, unit pairs
        """
        uid = kwargs.pop("uid", None)
        meta = kwargs.pop("meta", None)
        name = kwargs.pop("name", None)
        dimensions = kwargs.pop("dimensions", None)
        units = kwargs.pop("dimensions", None)
        super(Frame, self).__init__(*args, **kwargs)
        self.uid = uid
        self.meta = meta
        self.name = name
        self.dimensions = dimensions
        self.units = units


class Field(pd.DataFrame, ABCBase):
    """
    A field is a :class:`~exa.core.data.Frame` that does not require explicit
    definition of its dimensions.

    Dimensions are defined using a function that accepts fixed parameters which
    defin the space. The :class:`~exa.core.data.Field` object itself stores
    field values; the function and parameters are stored as metadata.
    """
    def __init__(self, *args, **kwargs):
        fn = kwargs.pop('fn', None)
        params = kwargs.pop('params', None)
        uid = kwargs.pop("uid", None)
        meta = kwargs.pop("meta", None)
        name = kwargs.pop("name", None)
        units = kwargs.pop("dimensions", None)


class FieldCollection(ABCBase):
    """
    Implicity, here, refers to the fact that unlike the
    :class:`~exa.core.frame.Frame`, values of the dimensions are not stored
    explicity. Instead, the 'frame' part of this data object is used to
    store function parameters that describe
    """
    def add_field(self, fn, params, values):
        """
        Add a new field to the :class:`~exa.core.data.Field` data object.

        Dimensions are dynamically generated by the function (fn) which
        accepts parameters (params) the define the space. Field values
        are given as values. This function doesn't return anything, it
        appends a new field to the field collection.

        Arg:
            fn: Function or string label to method accepting params
            params: A collection of parameters accepted by fn

        """
        pass

    def __init__(self, name=None, uid=None, meta=None, *fields):
        super(FieldCollection, self).__init__(name=name, uid=uid, meta=meta)
        for field in fields:
            self.add_field(field)




#import six
#import pandas as pd
#from uuid import UUID, uuid4
#from abc import abstractproperty
#from exa.typed import Meta
#
#
#index_types = (pd.core.index.RangeIndex, pd.core.index.Int64Index,
#               pd.core.index.CategoricalIndex)
#
#
#class GenericMeta(Meta):
#    """
#    Metaclass for generic data objects.
#
#    All data objects must have a unique id. This identifier is used by
#    :class:`~exa.core.container.Container` objects to disambiguate different
#    data objects with similar (or same) names, dimensions, and attributes
#    """
#    uid = UUID
#
#
## Default dat objects rely on pandas machinery
#class ABCData(GenericMeta, pd.core.generic.NDFrame):
#    """Abstract base class for default data objects."""
#    _metadata = ["name", "uid", "units"]
#
#    @property
#    def metadata(self):
#        """Return a dictionary of metadata."""
#        return {name: getattr(self, name) for name in self._metadata}
#
#    @property
#    def features(self):
#        """Return a list of feature names."""
#        if self.dims is not None:
#            return [col for col in self.columns if col not in self.dims]
#        return [col for col in self.columns]
#
#    @property
#    def dimensions(self):
#        """Return a list of dimension names."""
#        if self.dims is None:
#            return []
#        return self.dims
#
#    @abstractproperty
#    def _constructor(self):
#        """Used by pandas to finalize object creation."""
#        pass
#
#    @classmethod
#    def _create_indexers(cls, indexers):
#        """Wrapper around :func:`~pandas.core.generic.NDFrame._create_indexer`."""
#        for name, indexer in indexers:
#            setattr(cls, name, None)
#            cls._create_indexer(name, indexer)
#
#
#class DataMeta(six.with_metaclass(enericMeta):
#    """Metaclass for :class:`~exa.core.data.Data`."""
#    _getters = ("compute", )
#    units = dict
#    dims = list
#
#
#class Data(six.with_metaclass(DataMeta, ABCData, pd.DataFrame)):
#    """A multiply featured, n-dimensional data object."""
#    def as_dimensional(self):
#        """Return a multi-indexed object with dimensions as indices."""
#        if self.dims is not None:
#            return self.reset_index().set_index(self.dims)
#
#    def __init__(self, *args, **kwargs):
#        uid = kwargs.pop('uid', uuid4())
#        units = kwargs.pop('units', None)
#        dims = kwargs.pop('dims', None)
#        super(Data, self).__init__(*args, **kwargs)
#        self.uid = uid
#        self.units = units
#        self.dims = dims
#        if not isinstance(self.index, index_types):
#            self.reset_index(inplace=True)
#        self.index.name = "idx"
#
#
#class BaseSectionIndexer(object):
#    def __init__(self, data):
#        self._data = data
#
#    def __getitem__(self, *args, **kwargs):
#        print(args, kwargs)
#
#
#class SectionIndexer(BaseSectionIndexer):
#    pass
#
#
#class ISectionIndexer(BaseSectionIndexer):
#    pass
#
#
#def get_indexers():
#    """Return a list of indexers."""
#    return [("sec", SectionIndexer), ("isec", ISectionIndexer)]
#
#
#ABCData._create_indexers(get_indexers())
