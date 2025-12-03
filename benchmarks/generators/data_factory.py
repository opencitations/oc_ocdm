"""
Data generation utilities for benchmarks.

Provides factory methods for creating realistic bibliographic data
following OpenCitations Data Model patterns.
"""

import random
import string
from typing import List, Optional, Tuple

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.graph.entities.bibliographic.bibliographic_resource import (
    BibliographicResource,
)
from oc_ocdm.graph.entities.bibliographic.agent_role import AgentRole
from oc_ocdm.graph.entities.identifier import Identifier
from oc_ocdm.support import create_date


FIRST_NAMES = [
    "John", "Jane", "Michael", "Emily", "David", "Sarah", "James", "Emma",
    "Robert", "Olivia", "William", "Sophia", "Richard", "Isabella", "Joseph",
    "Mia", "Thomas", "Charlotte", "Charles", "Amelia", "Christopher", "Harper",
    "Daniel", "Evelyn", "Matthew", "Abigail", "Anthony", "Elizabeth"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez"
]

JOURNAL_NAMES = [
    "Nature", "Science", "Cell", "The Lancet", "JAMA", "BMJ", "PNAS",
    "Physical Review Letters", "Journal of the American Chemical Society",
    "Angewandte Chemie", "Chemical Reviews", "Advanced Materials",
    "Nature Communications", "Scientific Reports", "PLOS ONE"
]

TITLE_WORDS = [
    "analysis", "study", "investigation", "approach", "method", "system",
    "model", "framework", "algorithm", "technique", "evaluation", "assessment",
    "review", "comparison", "development", "implementation", "design",
    "optimization", "characterization", "synthesis", "application", "effect",
    "impact", "role", "mechanism", "structure", "function", "dynamics",
    "properties", "performance", "novel", "new", "improved", "enhanced",
    "efficient", "robust", "scalable", "comprehensive", "systematic"
]


class DataFactory:
    """
    Factory for generating realistic bibliographic data for benchmarks.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the data factory.

        Args:
            seed: Random seed for reproducible data generation.
        """
        if seed is not None:
            random.seed(seed)

    @staticmethod
    def random_doi(index: int = 0) -> str:
        """Generate a random DOI string."""
        prefix = random.choice(["10.1000", "10.1234", "10.5678", "10.9999"])
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}/bench.{index}.{suffix}"

    @staticmethod
    def random_orcid() -> str:
        """Generate a random ORCID identifier."""
        parts = [
            "".join(random.choices(string.digits, k=4))
            for _ in range(4)
        ]
        return "-".join(parts)

    @staticmethod
    def random_author_name() -> Tuple[str, str]:
        """Generate random given and family names."""
        return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)

    @staticmethod
    def random_title() -> str:
        """Generate a random article title."""
        words = random.sample(TITLE_WORDS, k=random.randint(5, 10))
        title = " ".join(words).capitalize()
        return f"A {title}"

    @staticmethod
    def random_journal() -> str:
        """Generate a random journal name."""
        return random.choice(JOURNAL_NAMES)

    @staticmethod
    def random_date(start_year: int = 2000, end_year: int = 2024) -> str:
        """Generate a random ISO 8601 date string."""
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return create_date([year, month, day])

    @staticmethod
    def random_pages() -> Tuple[str, str]:
        """Generate random start and end page numbers."""
        start = random.randint(1, 500)
        end = start + random.randint(5, 30)
        return str(start), str(end)

    @staticmethod
    def random_volume() -> str:
        """Generate a random volume number."""
        return str(random.randint(1, 100))

    @staticmethod
    def random_issue() -> str:
        """Generate a random issue number."""
        return str(random.randint(1, 12))

    def create_author(
        self,
        graph_set: GraphSet,
        resp_agent: str,
        index: int = 0
    ) -> AgentRole:
        """
        Create an author with ResponsibleAgent and AgentRole.

        Args:
            graph_set: The GraphSet to add entities to.
            resp_agent: The responsible agent URI.
            index: Index for unique generation.

        Returns:
            AgentRole for the author.
        """
        given_name, family_name = self.random_author_name()

        ra = graph_set.add_ra(resp_agent)
        ra.has_given_name(given_name)
        ra.has_family_name(family_name)
        ra.has_name(f"{given_name} {family_name}")

        orcid_id = self.create_identifier(graph_set, resp_agent, "orcid", index)
        ra.has_identifier(orcid_id)

        ar = graph_set.add_ar(resp_agent)
        ar.create_author()
        ar.is_held_by(ra)

        return ar

    def create_editor(
        self,
        graph_set: GraphSet,
        resp_agent: str,
        index: int = 0
    ) -> AgentRole:
        """
        Create an editor with ResponsibleAgent and AgentRole.

        Args:
            graph_set: The GraphSet to add entities to.
            resp_agent: The responsible agent URI.
            index: Index for unique generation.

        Returns:
            AgentRole for the editor.
        """
        given_name, family_name = self.random_author_name()

        ra = graph_set.add_ra(resp_agent)
        ra.has_given_name(given_name)
        ra.has_family_name(family_name)
        ra.has_name(f"{given_name} {family_name}")

        orcid_id = self.create_identifier(graph_set, resp_agent, "orcid", index)
        ra.has_identifier(orcid_id)

        ar = graph_set.add_ar(resp_agent)
        ar.create_editor()
        ar.is_held_by(ra)

        return ar

    def create_publisher(
        self,
        graph_set: GraphSet,
        resp_agent: str
    ) -> AgentRole:
        """
        Create a publisher with ResponsibleAgent and AgentRole.

        Args:
            graph_set: The GraphSet to add entities to.
            resp_agent: The responsible agent URI.

        Returns:
            AgentRole for the publisher.
        """
        publishers = [
            "Springer Nature", "Elsevier", "Wiley", "Taylor & Francis",
            "SAGE Publications", "Oxford University Press", "Cambridge University Press"
        ]

        ra = graph_set.add_ra(resp_agent)
        ra.has_name(random.choice(publishers))

        ar = graph_set.add_ar(resp_agent)
        ar.create_publisher()
        ar.is_held_by(ra)

        return ar

    def create_identifier(
        self,
        graph_set: GraphSet,
        resp_agent: str,
        scheme: str = "doi",
        index: int = 0
    ) -> Identifier:
        """
        Create an identifier entity.

        Args:
            graph_set: The GraphSet to add entities to.
            resp_agent: The responsible agent URI.
            scheme: Identifier scheme (doi, orcid, pmid, etc.).
            index: Index for unique generation.

        Returns:
            Identifier entity.
        """
        id_entity = graph_set.add_id(resp_agent)

        if scheme == "doi":
            id_entity.create_doi(self.random_doi(index))
        elif scheme == "orcid":
            id_entity.create_orcid(self.random_orcid())
        elif scheme == "pmid":
            id_entity.create_pmid(str(random.randint(10000000, 99999999)))
        elif scheme == "issn":
            issn = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            id_entity.create_issn(issn)

        return id_entity

    def create_journal_article(
        self,
        graph_set: GraphSet,
        resp_agent: str,
        index: int = 0,
        num_authors: int = 2,
        with_identifiers: bool = True,
        with_pages: bool = True
    ) -> BibliographicResource:
        """
        Create a complete journal article with authors and identifiers.

        This follows the typical OpenCitations Data Model pattern.

        Args:
            graph_set: The GraphSet to add entities to.
            resp_agent: The responsible agent URI.
            index: Index for unique generation.
            num_authors: Number of authors to create.
            with_identifiers: Whether to create identifiers (DOI).
            with_pages: Whether to create page information.

        Returns:
            BibliographicResource for the article.
        """
        br = graph_set.add_br(resp_agent)
        br.has_title(self.random_title())
        br.has_pub_date(self.random_date())
        br.create_journal_article()

        prev_ar = None
        for i in range(num_authors):
            ar = self.create_author(graph_set, resp_agent, index * 100 + i)
            br.has_contributor(ar)
            if prev_ar is not None:
                prev_ar.has_next(ar)
            prev_ar = ar

        if with_identifiers:
            doi_id = self.create_identifier(graph_set, resp_agent, "doi", index)
            br.has_identifier(doi_id)

        if with_pages:
            re = graph_set.add_re(resp_agent)
            start_page, end_page = self.random_pages()
            re.has_starting_page(start_page)
            re.has_ending_page(end_page)
            br.has_format(re)

        return br

    def create_journal_hierarchy(
        self,
        graph_set: GraphSet,
        resp_agent: str,
        index: int = 0
    ) -> Tuple[BibliographicResource, BibliographicResource, BibliographicResource]:
        """
        Create a journal > volume > issue hierarchy.

        Args:
            graph_set: The GraphSet to add entities to.
            resp_agent: The responsible agent URI.
            index: Index for unique generation.

        Returns:
            Tuple of (journal_br, volume_br, issue_br).
        """
        journal_br = graph_set.add_br(resp_agent)
        journal_br.has_title(self.random_journal())
        journal_br.create_journal()

        issn_id = self.create_identifier(graph_set, resp_agent, "issn", index)
        journal_br.has_identifier(issn_id)

        volume_br = graph_set.add_br(resp_agent)
        volume_br.has_number(self.random_volume())
        volume_br.create_volume()
        volume_br.is_part_of(journal_br)

        issue_br = graph_set.add_br(resp_agent)
        issue_br.has_number(self.random_issue())
        issue_br.create_issue()
        issue_br.is_part_of(volume_br)

        return journal_br, volume_br, issue_br

    def create_complete_bibliographic_record(
        self,
        graph_set: GraphSet,
        resp_agent: str,
        index: int = 0,
        num_authors: int = 2
    ) -> BibliographicResource:
        """
        Create a complete bibliographic record with full hierarchy.

        Creates:
        - 1 article BR + title + date + type
        - N author ARs + RAs with names
        - 1 DOI identifier
        - 1 RE with pages
        - Journal > Volume > Issue hierarchy (3 BRs)
        - Publisher AR + RA

        Total entities per record: 1 + 2N + 1 + 1 + 3 + 2 = 8 + 2N

        Args:
            graph_set: The GraphSet to add entities to.
            resp_agent: The responsible agent URI.
            index: Index for unique generation.
            num_authors: Number of authors to create.

        Returns:
            BibliographicResource for the article.
        """
        article_br = self.create_journal_article(
            graph_set, resp_agent, index, num_authors,
            with_identifiers=True, with_pages=True
        )

        journal_br, _, issue_br = self.create_journal_hierarchy(
            graph_set, resp_agent, index
        )

        article_br.is_part_of(issue_br)

        ar = self.create_publisher(graph_set, resp_agent)
        journal_br.has_contributor(ar)

        return article_br

    def populate_graph_set(
        self,
        graph_set: GraphSet,
        resp_agent: str,
        num_records: int,
        num_authors_per_record: int = 2
    ) -> List[BibliographicResource]:
        """
        Populate a GraphSet with multiple bibliographic records.

        Args:
            graph_set: The GraphSet to populate.
            resp_agent: The responsible agent URI.
            num_records: Number of records to create.
            num_authors_per_record: Authors per record.

        Returns:
            List of created article BibliographicResources.
        """
        articles = []
        for i in range(num_records):
            article = self.create_complete_bibliographic_record(
                graph_set, resp_agent, i, num_authors_per_record
            )
            articles.append(article)
        return articles