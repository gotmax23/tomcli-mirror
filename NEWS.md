<!--
Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
SPDX-License-Identifier: MIT
-->

NEWS
=======

## 0.6.0 - 2024-03-28 <a id='0.6.0'></a>

### Added

- `cli main`: add command description
- `cli set`: allow passing multiple values to the append command
- `cli`: support `python -m tomcli`
- `doc`: add manpages
- `doc`: add mkdocs configuration

### Fixed

- `cli set`: remove unnecessary `resilient_parsing` conditional
- `cli get`: properly handle `FormatterError` exceptions

## 0.5.0 - 2023-12-14 <a id='0.5.0'></a>

### Added

- README.md: add usage examples
- tomcli.spec: add smoke tests
- tomcli.spec: add minimal py3_test_envvars def for EPEL 9

### Changed

- build: use flit_core instead of hatchling as build backend
- cli: use click instead of typer as CLI framework

### Fixed

- cli: allow accessing keys containing dots

## 0.4.0 - 2023-12-02 <a id='0.4.0'></a>

### Added

- cli set: add `true` subcommand
- cli set: add `false` subcommand
- cli: add `--version` argument
- cli: add parent `tomcli` command with `set` and `get` subcommands
- cli get: add `-F` / `--formatter` arg to customize output
- cli: add `tomcli-formatters` / `tomcli formatters` command to list
  available `get` formatters

## 0.3.0 - 2023-09-07 <a id='0.3.0'></a>

### Added

- cli set: add `lists delitem` subcommand

### Fixed

- Fully drop support for Python 3.7.
  Support for 3.7 was officially removed in the previous release, but the
  metadata was not updated correctly.

## 0.2.0 - 2023-09-01 <a id='0.2.0'></a>

### Added

- add py.typed file
- declare support for Python 3.12
- cli set: add missing help messages
- cli set: add `lists replace` and `lists str` commands

### Fixed

- cli: improve error handling

### Removed

- drop support for Python 3.7

## 0.1.2 - 2023-05-20 <a id='0.1.2'></a>

### Fixed

- tomcli-set: fix typo in error message
- tomcli-set: fix recursive dictionary creation

## 0.1.1 - 2023-05-03 <a id='0.1.1'></a>

### Added

- tomcli.spec: add gnupg2 BuildRequires
- tomcli.spec: add missing extras subpackages
- tomcli.spec: include NEWS.md

### Fixed

- **tomcli-get: fix broken toml backend fallback**
- fix pronunciation description in packaging metadata and README

## 0.1.0 - 2023-04-14 <a id='0.1.0'></a>

### Added

- cli: add tomcli-set subcommand
- packaging: add RPM specfile
- packaging: wire up automated copr builds.
- packaging: include shell completions in the RPM specfile
- internal: cleanup and increase tomlkit compat.
  Dev builds are available at `gotmax23/tomcli-dev` and releases at `gotmax23/tomcli`.

## 0.0.0 - 2023-04-13 <a id='0.0.0'></a>

Initial release of tomcli, a CLI tool for working with TOML files.
Pronounced "tohm-clee."
Currently, tomcli only provides ` tomcli-get` command but more are planned!
