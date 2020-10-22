#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.
from __future__ import annotations

from functools import wraps
from typing import Callable, Any
from rdflib import URIRef
from oc_ocdm import GraphEntity


def accepts_only(param_type: str):
    def accepts_only_decorator(function: Callable):

        @wraps(function)
        def accepts_only_wrapper(self, param: Any = None):
            lowercase_type = param_type.lower()
            if param is None or \
                    (lowercase_type == 'literal' and type(param) == str) or \
                    (lowercase_type == 'thing' and type(param) == URIRef) or \
                    (lowercase_type == 'date' and type(param) in (list, tuple)) or \
                    (isinstance(param, GraphEntity) and param.short_name == lowercase_type):
                function(self, param)
            else:
                raise TypeError('[%s.%s] Expected argument type: %s. Provided argument type: %s.' %
                                (self.__class__.__name__, function.__name__, lowercase_type, type(param).__name__))

        return accepts_only_wrapper
    return accepts_only_decorator
