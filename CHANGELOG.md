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
