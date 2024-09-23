TOMCLI-SET-ARRAYS(1)

# NAME

tomcli-set arrays — CLI for working with TOML files. Pronounced "tom clee."

# SYNOPSIS

*\[tomcli-set \| tomcli set]* [_GLOBAL OPTIONS_] _PATH_ arrays *COMMAND* [_OPTIONS_] [_ARGUMENTS_]

*\[tomcli-set \| tomcli set]* ... *arrays* [*COMMAND*] --help

# DESCRIPTION

The *tomcli-set arrays* subcommand supports modifying arrays in TOML files.

*tomcli-set lists* is available as an alias for backwards compatibility,
but *arrays* is preferred, as it follows the TOML spec's terminology.
There are no plans to remove the lists subcommand;
backwards compatibility is important to the tomcli project.

# ARGUMENTS

*PATH*
	Path to a TOML file to read. Use '-' to read from stdin.
	Set to _..._ when calling *--help* for a subcommand.
*SELECTOR*
	A dot separated map to a key in the TOML mapping. ++
	Example: 'section1.subsection.value' or '"key.with.dots".abc'
*VALUE*
	Value to set
*PATTERN*
	Pattern against which to match strings
	Defaults to _regex_ but can be changed with the *--type* option.
	The pattern must match the full string.
*REPL*
	Replacement string (used by *replace* subcommand).
	Supports Python regex expansions (e.g. *\\1*) when
	*--type* is set to _regex_ (i.e., the default value).

# GLOBAL OPTIONS

*--version*
	Show the version and exit.
*--writer* <tomli_w|tomlkit>
	Library to use to write TOML files.
*--reader* <tomli|tomlkit>
	Library to use to write TOML files.
	Defaults to tomlkit and falls back to tomli/tomllib if tomlkit is unavailable.

# OPTIONS

*-t* / *--type* <_regex_|_fnmatch_> (default: _regex_)
	Matcher type.
	Python regexes and fnmatch(3)-style patterns are supported.
*--first* / *--no-first* (default: _no-first_)
	Only modify the first *PATTERN* match

*--key* <SELECTOR PATTERN>
	Only applies to the *delitem* subcommand.
	See the delitem documentation below.

# COMMANDS

## append

Add a string value to a TOML array

```
tomcli-set [GLOBAL OPTIONS] PATH arrays append [OPTIONS] SELECTOR VALUE 
tomcli-set ... arrays append --help
```

## delitem

Delete string values in a TOML array.
SELECTOR matches the path to the array and PATTERN matches strings within the
array that should be deleted.
Items that are not a string will be ignored.

The *--key* option be used to remove values from an array that contains
tables (i.e., key-value pairs) instead of strings.
Then, the KEY selector is looked up in each table and the respective value is
matched against PATTERN.
See https://todo.sr.ht/~gotmax23/tomcli/9 for a more detailed description and
rationale.

```
tomcli-set [GLOBAL OPTIONS] PATH arrays delitem [OPTIONS] SELECTOR PATTERN
tomcli-set ... arrays delitem --help
```

## replace

Replace string values in a TOML list with other string values

```
tomcli-set [GLOBAL OPTIONS] PATH arrays replace [OPTIONS] SELECTOR PATTERN REPL
tomcli-set ... arrays replace --help
```


## str

Create a TOML list of strings

```
tomcli-set [GLOBAL OPTIONS] PATH arrays str [VALUE...]
tomcli-set ... arrays str --help
```


# SEE ALSO

tomcli(1), tomcli-formatters(1), tomcli-set(1), tomcli-set(1)
