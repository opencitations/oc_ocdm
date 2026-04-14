#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2024-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, TypeVar, cast

from oc_ocdm.abstract_entity import AbstractEntity

if TYPE_CHECKING:
    from typing import Callable
F = TypeVar('F', bound='Callable[..., object]')


def accepts_only(param_type: str) -> Callable[[F], F]:
    """
    A decorator that can be applied to the entity methods such as setters and removers
    when they accept a parameter. It enforces the right parameter type by raising a
    ``TypeError`` when the parameter is not None but its type is not the expected one.

    The expected type can be expressed through a short string:

      * '_dataset_' for the ``Dataset`` entities;
      * the OCDM short name in case of any other entity (e.g. 'br' for ``BibliographicResource``).

    :param param_type: A short string representing the expected type
    :type param_type: str
    """
    def accepts_only_decorator(function: F) -> F:

        @wraps(function)
        def accepts_only_wrapper(self: object, param: object = None, **kwargs: object) -> object:
            lowercase_type = param_type.lower()
            if param is None or \
                    (isinstance(param, AbstractEntity) and param.short_name == lowercase_type):
                return function(self, param, **kwargs)
            else:
                raise TypeError('[%s.%s] Expected argument type: %s. Provided argument type: %s.' %
                                (self.__class__.__name__, function.__name__, lowercase_type, type(param).__name__))

        return cast(F, accepts_only_wrapper)
    return accepts_only_decorator