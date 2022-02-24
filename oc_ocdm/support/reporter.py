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
        cur_sentence: str = self.prefix + sentence
        self.last_sentence = cur_sentence
        self.last_article.append(cur_sentence)
        if self.print_sentences and print_this_sentence:
            print(cur_sentence)

    def get_last_sentence(self) -> Optional[str]:
        return self.last_sentence

    def get_articles_as_string(self) -> str:
        result: str = ""
        for article in self.articles:
            for sentence in article:
                result += sentence + "\n"
            result += "\n"
        return result

    def write_file(self, file_path) -> None:
        with open(file_path, 'wt', encoding='utf-8') as f:
            f.write(self.get_articles_as_string())

    def is_empty(self) -> bool:
        return self.last_sentence is None
