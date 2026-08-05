# [1.8.0](https://github.com/JohannGaviria/verbose-potato/compare/v1.7.1...v1.8.0) (2026-08-05)


### Bug Fixes

* **auth:** allow startup when first librarian already exists ([8b7db16](https://github.com/JohannGaviria/verbose-potato/commit/8b7db16f6a8dd5ebd01bb7373d347b41028bf949))
* **tests:** isolate database state between e2e and integration tests ([3390c9b](https://github.com/JohannGaviria/verbose-potato/commit/3390c9b75893713e81a9c22990dec2ebe11ff0d0))
* **tests:** isolate db schema fixture and e2e pollution ([96e65c5](https://github.com/JohannGaviria/verbose-potato/commit/96e65c5ad0b4f5f1cedfe31868b586e07114c358))
* **tests:** modularize database fixture logic ([699aa79](https://github.com/JohannGaviria/verbose-potato/commit/699aa792a85ec208cb76730ad4ac3b43a079d0e6))


### Features

* **auth:** add find_by_email method to SQLAlchemyUserRepositoryAdapter ([a064c4f](https://github.com/JohannGaviria/verbose-potato/commit/a064c4f5c1928cbdb634872698b3d6c97fe72cc0))
* **auth:** add verify method to password hash outbound port ([9101600](https://github.com/JohannGaviria/verbose-potato/commit/91016009d8b4b5c13fed1c415297d654895cceae))
* **auth:** implement argon2 password hashing adapter ([07b8071](https://github.com/JohannGaviria/verbose-potato/commit/07b8071c10db86d5727f75b9a4888e18e5e2ea57))
* **auth:** implement argon2 password verification ([35cb815](https://github.com/JohannGaviria/verbose-potato/commit/35cb815888927e8f4dcd099355b243d10e1546a5))
* **auth:** implement authentication module ([0b33b83](https://github.com/JohannGaviria/verbose-potato/commit/0b33b8377ecb3aaf5b9770ca09a29fc91779bdbf)), closes [#1](https://github.com/JohannGaviria/verbose-potato/issues/1) [#2](https://github.com/JohannGaviria/verbose-potato/issues/2) [#3](https://github.com/JohannGaviria/verbose-potato/issues/3)
* **auth:** implement automatic first librarian registration ([8444bf3](https://github.com/JohannGaviria/verbose-potato/commit/8444bf38dfefc7b07610ac4cfac9af416c8e3053))
* **auth:** implement automatic librarian registration use case ([4f3fb2c](https://github.com/JohannGaviria/verbose-potato/commit/4f3fb2c3bcdeae70de82f32efb5bdb41590929f4))
* **auth:** implement domain models and ports for token generation ([e12728a](https://github.com/JohannGaviria/verbose-potato/commit/e12728a05c2b62fd0725796cdae55b08a632a934))
* **auth:** implement login endpoint ([7670a2f](https://github.com/JohannGaviria/verbose-potato/commit/7670a2f3e8cd9225f8d896d5fa472b4da73da7f5))
* **auth:** implement login use case ([c6981a0](https://github.com/JohannGaviria/verbose-potato/commit/c6981a0bf7fea6857d10ff3067ab6651d76e1c8c))
* **auth:** implement new user registration API ([7102dfb](https://github.com/JohannGaviria/verbose-potato/commit/7102dfb4db3690df4d167c41c1a0c129d1667730))
* **auth:** implement new user registration use case ([60c2144](https://github.com/JohannGaviria/verbose-potato/commit/60c2144f794dedcad888ef6e750b1947ab9a49ab))
* **auth:** implement pyjwt adapter for token generation ([2e06473](https://github.com/JohannGaviria/verbose-potato/commit/2e0647337d61d1bf657a3cbf19eb0f0822d611ed))
* **auth:** implement SQLAlchemy user unit of work adapter ([33dc1ca](https://github.com/JohannGaviria/verbose-potato/commit/33dc1ca890d5f7d98af2c3dd23182ad7cb332c25))
* **auth:** implement US-RF-001: Automatic LIBRARIAN registration at application startup [#1](https://github.com/JohannGaviria/verbose-potato/issues/1) ([b9f6198](https://github.com/JohannGaviria/verbose-potato/commit/b9f6198c44eff7e5df3a7f74c0d94e328c2f05a4))
* **auth:** implement US-RF-002: New user registration [#2](https://github.com/JohannGaviria/verbose-potato/issues/2) ([dab5480](https://github.com/JohannGaviria/verbose-potato/commit/dab5480cf749fddc50551dbb5443805f65b0602b))
* **auth:** implement US-RF-003: login [#3](https://github.com/JohannGaviria/verbose-potato/issues/3) ([0da7ca1](https://github.com/JohannGaviria/verbose-potato/commit/0da7ca1ad91a12b999a5554b1533688820cd4962))
* **auth:** implement user entity and value objects ([0808758](https://github.com/JohannGaviria/verbose-potato/commit/0808758941b4aa4380e6d5075907e3f43a2b861b))
* **auth:** implement user model in database ([e26942a](https://github.com/JohannGaviria/verbose-potato/commit/e26942a6e53c8407d6686506f0fd851d807e6e90))
* **auth:** implement user persistence layer ([266a847](https://github.com/JohannGaviria/verbose-potato/commit/266a8471c458f677415ec621b7713ff72ac4c5a8))

## [1.7.1](https://github.com/JohannGaviria/verbose-potato/compare/v1.7.0...v1.7.1) (2026-07-17)


### Bug Fixes

* add coverage configuration ([516699a](https://github.com/JohannGaviria/verbose-potato/commit/516699aaaeb0f9753bf16ecb30c0d277c68eedce))

# [1.7.0](https://github.com/JohannGaviria/verbose-potato/compare/v1.6.0...v1.7.0) (2026-07-17)


### Bug Fixes

* **CI:** update github plugin configuration in release workflow ([36d6841](https://github.com/JohannGaviria/verbose-potato/commit/36d6841a2371c74a16a9c897b53368a264f57095))


### Features

* **CI:** automate version synchronization via semantic-release ([8030c85](https://github.com/JohannGaviria/verbose-potato/commit/8030c852309498b3d4ac3537b061de80b4d0a529))

# [1.6.0](https://github.com/JohannGaviria/verbose-potato/compare/v1.5.0...v1.6.0) (2026-07-17)


### Features

* **release:** bump version to 1.5.0 ([b64e830](https://github.com/JohannGaviria/verbose-potato/commit/b64e83040d7609a4f629392b7a7ca9ebf67e6ab6))

# [1.5.0](https://github.com/JohannGaviria/verbose-potato/compare/v1.4.0...v1.5.0) (2026-07-16)


### Features

* **release:** bump version to 1.4.0 ([fdd652e](https://github.com/JohannGaviria/verbose-potato/commit/fdd652e48ac73a53408c9fef5b3ff3c839ee1914))

# [1.4.0](https://github.com/JohannGaviria/verbose-potato/compare/v1.3.0...v1.4.0) (2026-07-16)


### Features

* **CD:** optimize semantic-release workflow and bump version ([a2efacb](https://github.com/JohannGaviria/verbose-potato/commit/a2efacb3d22fa2b26dbe585e3e946caf743ce30e))
* **ci:** decouple release and image publishing workflows ([003eb44](https://github.com/JohannGaviria/verbose-potato/commit/003eb44a4b4dfe9549f60b1e35d49556d4b31d4c))

# [1.3.0](https://github.com/JohannGaviria/verbose-potato/compare/v1.2.0...v1.3.0) (2026-07-16)


### Features

* **api:** add presentation layer components and correlation middleware ([0fd230f](https://github.com/JohannGaviria/verbose-potato/commit/0fd230f5b535d877ad087529f732f67678aa64f2))

# [1.2.0](https://github.com/JohannGaviria/verbose-potato/compare/v1.1.0...v1.2.0) (2026-07-16)


### Features

* **shared:** implement unit of work port and base persistence models ([c253a93](https://github.com/JohannGaviria/verbose-potato/commit/c253a93df7320225767b02de3e603c5ca480ff2a))

# [1.1.0](https://github.com/JohannGaviria/verbose-potato/compare/v1.0.0...v1.1.0) (2026-07-16)


### Features

* **shared:** add redis cache implementation via hexagonal architecture ([96a37fd](https://github.com/JohannGaviria/verbose-potato/commit/96a37fd6b302b79405c380c4116bb9352bffd5f8))

# 1.0.0 (2026-07-16)


### Features

* **shared:** implement structured logging via hexagonal architecture ([d803313](https://github.com/JohannGaviria/verbose-potato/commit/d8033130fbf15eea0b0acf2fab5e7b47bfe44dae))
