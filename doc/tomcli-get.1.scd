TOMCLI-GET(1)

# NAME

*tomcli-get* -- CLI for working with TOML files. Pronounced "tom clee."

# SYNOPSIS

*\[tomcli-get \| tomcli get]* [OPTIONS] PATH [SELECTOR]

# DESCRIPTION

The *tomcli-get* subcommand supports querying TOML files.

# ARGUMENTS

*PATH*
	Path to a TOML file to read. Use '-' to read from stdin.
*[SELECTOR]* (default: _._)
	A dot separated map to a key in the TOML mapping. ++
	Example: 'section1.subsection.value' or '"key.with.dots".abc'

# OPTIONS

*--version*
	Show the version and exit.
*--writer* <tomli_w|tomlkit>
	Library to use to write TOML files.
*--reader* <tomli|tomlkit>
	Library to use to write TOML files.
	Defaults to tomlkit and falls back to tomli/tomllib if tomlkit is unavailable.
*-F* / *--formatter* <default: _default_>
	Which output formatter to use.
	See tomcli-formatters(1) for a full list.


# SEE ALSO

tomcli(1), tomcli-formatters(1), tomcli-set(1)
