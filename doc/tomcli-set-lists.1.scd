TOMCLI-SET-LISTS(1)

# NAME

tomcli-set lists -- CLI for working with TOML files. Pronounced "tom clee."

# SYNOPSIS

*\[tomcli-set \| tomcli set]* [GLOBAL OPTIONS] PATH lists COMMAND [OPTIONS] [ARGUMENTS]

*\[tomcli-set \| tomcli set]* ... lists [COMMAND] --help

# DESCRIPTION

The *tomcli-set lists* subcommand supports modifying lists in TOML files.

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
	Support Python regex expansions (e.g. *\\1*) when 

# GLOBAL OPTIONS

*--version*
	Show the version and exit.
*--writer* <tomli_w|tomlkit>
	Library to use to write TOML files.
*--reader* <tomli|tomlkit>
	Library to use to write TOML files.
	Defaults to tomlkit and falls back to tomli/tomllib if tomlkit is unavailable.

# OPTIONS

*-t* / *--type* <_regex_|_fnmatch_>
	Matcher type.
	Python regexes and fnmatch(3)-style patterns are supported.
*--first*
	Only modify the first *PATTERN* match

# COMMANDS

## append

Add a string value to a TOML list

```
tomcli-set [GLOBAL OPTIONS] PATH append [OPTIONS] SELECTOR VALUE 
tomcli-set ... append --help
```

## delitem

Delete string values from a TOML file

```
tomcli-set [GLOBAL OPTIONS] PATH lists delitem [OPTIONS] SELECTOR PATTERN
tomcli-set ... lists delitem --help
```

## replace

Replace string values in a TOML list with other string values

```
tomcli-set [GLOBAL OPTIONS] PATH lists replace [OPTIONS] SELECTOR PATTERN REPL
tomcli-set ... lists replace --help
```


## str

Create a TOML list of strings

```
tomcli-set [GLOBAL OPTIONS] PATH lists str [VALUE...]
tomcli-set ... lists str --help
```


# SEE ALSO

tomcli(1), tomcli-formatters(1), tomcli-set(1), tomcli-set(1)
