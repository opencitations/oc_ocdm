#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2025-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional


class Reporter(object):
    """This class is used as a metaphoric agent being a reporter"""

    def __init__(self, print_sentences: bool = True, prefix: str = "") -> None:
        self.articles: List[List[str]] = []
        self.last_article: Optional[List[str]] = None
        self.last_sentence: Optional[str] = None
        self.print_sentences: bool = print_sentences
        self.prefix: str = prefix

    def new_article(self) -> None:
        if self.last_article is None or len(self.last_article) > 0:
            self.last_article = []
            self.last_sentence = None
            self.articles.append(self.last_article)
            if self.print_sentences and len(self.last_article) > 0:
                print("\n")

    def add_sentence(self, sentence: str, print_this_sentence: bool = True) -> None:
        assert self.last_article is not None
        cur_sentence: str = self.prefix + sentence
        self.last_sentence = cur_sentence
        self.last_article.append(cur_sentence)
        if self.print_sentences and print_this_sentence:
            print(cur_sentence)

    def get_last_sentence(self) -> Optional[str]:
        return self.last_sentence

    def get_articles_as_string(self) -> str:
        parts = []
        for article in self.articles:
            for sentence in article:
                parts.append(sentence)
                parts.append("\n")
            parts.append("\n")
        return ''.join(parts)

    def write_file(self, file_path) -> None:
        with open(file_path, 'wt', encoding='utf-8') as f:
            f.write(self.get_articles_as_string())

    def is_empty(self) -> bool:
        return self.last_sentence is None
