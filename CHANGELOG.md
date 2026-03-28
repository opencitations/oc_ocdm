# [10.0.0](https://github.com/opencitations/oc_ocdm/compare/9.4.4...10.0.0) (2026-03-28)


* fix(graph)!: make res_type a required parameter in GraphEntity ([0cf909b](https://github.com/opencitations/oc_ocdm/commit/0cf909b06857f5e5e217d28264584a9e3dfa28b6))
* refactor!: fix type annotations and restructure metadata layer ([fa2b3f4](https://github.com/opencitations/oc_ocdm/commit/fa2b3f4c0e2fce2ebb159a42c305c82dcb32034a))


### BREAKING CHANGES

* MetadataEntity.__init__ now requires res_type as a
positional parameter. Storer.upload_all drops prepare_bulk_load and
bulk_load_dir. serialize_graph_to_nquads and get_separated_queries are
removed from query_utils. SqliteCounterHandler methods align with the
CounterHandler base signature.
* GraphEntity.__init__ signature changed — res_type is
now the third positional argument (required), res is fourth (optional).

<!--
SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>

SPDX-License-Identifier: ISC
-->

## [9.4.4](https://github.com/opencitations/oc_ocdm/compare/9.4.3...9.4.4) (2026-03-13)


### Bug Fixes

* normalize RDF literals to xsd:string and tighten type annotations ([2164e19](https://github.com/opencitations/oc_ocdm/commit/2164e19e74e338bdfd1256d35fb79cbe4093e742))

## [9.4.3](https://github.com/opencitations/oc_ocdm/compare/9.4.2...9.4.3) (2025-12-06)


### Bug Fixes

* **sparql:** add query chunking to prevent oversized SPARQL requests ([7b28aea](https://github.com/opencitations/oc_ocdm/commit/7b28aeaaf3bfc31c3707068b08fd2fe285c47f4c))

## [9.4.2](https://github.com/opencitations/oc_ocdm/compare/9.4.1...9.4.2) (2025-12-05)


### Bug Fixes

* **sparql:** migrate from SPARQLWrapper to sparqlite ([a2b8957](https://github.com/opencitations/oc_ocdm/commit/a2b8957e45b81ef6830b7ca22fc82386e17cd8a8))

## [9.4.1](https://github.com/opencitations/oc_ocdm/compare/9.4.0...9.4.1) (2025-12-04)


### Bug Fixes

* **query_utils:** replace Graph objects with sets in _compute_graph_changes ([9dbd09e](https://github.com/opencitations/oc_ocdm/commit/9dbd09e118fdbac8f426fad6b94ee732c355e52b))
* **storer:** remove unnecessary Dataset reconstruction in _store_in_file ([5091653](https://github.com/opencitations/oc_ocdm/commit/509165316447a5e013a81c44f818e3c2942e71e5))
* **storer:** skip JSON parsing when context_map is empty ([334c319](https://github.com/opencitations/oc_ocdm/commit/334c3191b15b95b6424339bd1e8ac624d85a0e91))
* **support:** optimize find_paths with single regex match ([e244b5b](https://github.com/opencitations/oc_ocdm/commit/e244b5be3b974a3c3f9bdfb2f5443c4d2e315c92))


### Performance Improvements

* **benchmarks:** add context caching benchmark and improve tooling ([f601489](https://github.com/opencitations/oc_ocdm/commit/f601489443b2710c1d67b514b0a80594b986bfe0))
* **support:** cache parse_uri results and refactor URI helper functions ([efbe372](https://github.com/opencitations/oc_ocdm/commit/efbe3725108b3f70deb9a6b8f96ed5701ed4fccd))

# [9.4.0](https://github.com/opencitations/oc_ocdm/compare/9.3.0...9.4.0) (2025-12-04)


### Bug Fixes

* **query_utils:** replace isomorphic graph comparison with set operations [release] ([5650079](https://github.com/opencitations/oc_ocdm/commit/56500794eca31ca7b2a28f4a86d15b4b2c4a3713))


### Features

* add benchmark infrastructure ([e357300](https://github.com/opencitations/oc_ocdm/commit/e357300c25129ab7d4d3412500d881c21cb8fe5e))

# [9.3.0](https://github.com/opencitations/oc_ocdm/compare/9.2.8...9.3.0) (2025-11-24)


### Bug Fixes

* simplify upload_all API with prepare_bulk_load parameter [release] ([52cdb76](https://github.com/opencitations/oc_ocdm/commit/52cdb767e0a0e402f048e14d1e49056439e8ad23))


### Features

* add optimized bulk upload workflow with N-Quads serialization ([7ffb219](https://github.com/opencitations/oc_ocdm/commit/7ffb219bc0f1c1a8526ce5492c018f57d1d22dda))

## [9.2.8](https://github.com/opencitations/oc_ocdm/compare/9.2.7...9.2.8) (2025-11-22)


### Bug Fixes

* use isomorphic comparison instead of == operator for graph equality [release] ([ad41548](https://github.com/opencitations/oc_ocdm/commit/ad415489fc00d1d0ea17c6807a5030d1f7529579))

## [9.2.7](https://github.com/opencitations/oc_ocdm/compare/9.2.6...9.2.7) (2025-11-22)


### Bug Fixes

* optimize O(n²) operations in entity getters and string operations [release] ([8886b65](https://github.com/opencitations/oc_ocdm/commit/8886b653075662e9179537e75fc12397194a81fb))
* optimize save_queries workflow for large datasets ([c3b2d6b](https://github.com/opencitations/oc_ocdm/commit/c3b2d6b78042639217d26b9db85e7ebe7faa700e))

## [9.2.6](https://github.com/opencitations/oc_ocdm/compare/9.2.5...9.2.6) (2025-11-13)


### Bug Fixes

* add multiprocessing support with pickle serialization ([348a88e](https://github.com/opencitations/oc_ocdm/commit/348a88ea41d400bca425814b5db271f68c4a658a))

## [9.2.5](https://github.com/opencitations/oc_ocdm/compare/9.2.4...9.2.5) (2025-11-13)


### Bug Fixes

* prevent race condition in directory creation [release] ([372872b](https://github.com/opencitations/oc_ocdm/commit/372872bc078f16034c5c4162f75abfb12986b891))

## [9.2.4](https://github.com/opencitations/oc_ocdm/compare/9.2.3...9.2.4) (2025-11-12)


### Bug Fixes

* relax redis dependency version constraint [release] ([a46d9ec](https://github.com/opencitations/oc_ocdm/commit/a46d9eceaa7ea1b93025605fcccb18ef0f1cc3e4))

## [9.2.3](https://github.com/opencitations/oc_ocdm/compare/9.2.2...9.2.3) (2025-11-12)


### Bug Fixes

* migrate from ConjunctiveGraph to Dataset for rdflib 7.4.0 ([7b3ecf1](https://github.com/opencitations/oc_ocdm/commit/7b3ecf13def722e149a91f9d1948c4d0ac089bcd))
* replace timestamp with content hash for saved SPARQL query filenames [release] ([96b4ffd](https://github.com/opencitations/oc_ocdm/commit/96b4ffdec962c64b7c67165b40cdf6c7bfd2411c))

## [9.2.2](https://github.com/opencitations/oc_ocdm/compare/9.2.1...9.2.2) (2025-05-30)


### Bug Fixes

* **ci:** update Docker setup in GitHub Actions workflow ([b21a206](https://github.com/opencitations/oc_ocdm/commit/b21a206cf43dde72c026273c9a99a097e9abbc8d))
