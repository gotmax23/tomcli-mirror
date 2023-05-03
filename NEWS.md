<!--
Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>

SPDX-License-Identifier: MIT
-->

NEWS
=======

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
