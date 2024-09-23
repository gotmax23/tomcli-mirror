TOMCLI-SET(1)

# NAME

tomcli-set — CLI for working with TOML files. Pronounced "tom clee."

# SYNOPSIS

*\[tomcli-set \| tomcli set]* [GLOBAL OPTIONS] PATH COMMAND [ARGUMENTS]

*\[tomcli-set \| tomcli set]* ... [COMMAND] --help


# DESCRIPTION

The *tomcli-set* subcommand supports modifying TOML files.

# ARGUMENTS

*PATH*
	Path to a TOML file to read. Use '-' to read from stdin.
	Set to _..._ when calling *--help* for a subcommand.
*SELECTOR*
	A dot separated map to a key in the TOML mapping. ++
	Example: 'section1.subsection.value' or '"key.with.dots".abc' or
	'array.5' (where 0 is an array index)
*VALUE*
	Value to set

## replace

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

## replace

*-t* / *--type* <_regex\_fullmatch_|_regex_|_regex\_partial_|_fnmatch_>
(default: _regex\_fullmatch_)
	Matcher type.

	- _regex\_fullmatch_: Equivalent to *re.fullmatch* in Python.
	  The regex must match the whole string.
	- _regex_: Alias for _regex\_fullmatch_
	- _regex\_partial_: Equivalent to *re.match* in Python. The regex
	  matching starts at the beginning of the string
	  but does not have to match all of it.
	- _fnmatch_: Use an *fnmatch(3)*-style pattern.
	  The glob must match the whole string.

# COMMANDS

## append

Add a string value to a TOML list

```
tomcli-set [GLOBAL OPTIONS] PATH append [OPTIONS] SELECTOR VALUE
tomcli-set ... append --help
```

## del

Delete a value from a TOML file

```
tomcli-set [GLOBAL OPTIONS] PATH del [OPTIONS] SELECTOR...
tomcli-set ... del --help
```

## true / false

Set a value in a TOML file to *true* or *false*.

```
tomcli-set [GLOBAL OPTIONS] PATH [true | false] [OPTIONS] SELECTOR
tomcli-set ... [true | false] --help
```


## str / int / float

Set a string or integer or float value in a TOML file.

```
tomcli-set [GLOBAL OPTIONS] PATH [str|int|float] SELECTOR VALUE
tomcli-set ... [str|int|float] --help
```

## replace

Perform a replacement on a string in a TOML file.
If PATTERN does not match the existing value and --not-required is not
passed, the command will fail.
If you simply wish to replace the value of a string field without first checking
that it matches an expected value, use the 'str' subcommand instead.

```
tomcli-set [GLOBAL OPTIONS] PATH replace [OPTIONS] SELECTOR PATTERN REPL
tomcli-set ... replace --help
```

## arrays

Subcommand to modify TOML arrays. See tomcli-set-arrays(1).

## lists

Alias to the arrays subcommand.


# SEE ALSO

tomcli(1), tomcli-formatters(1), tomcli-get(1), tomcli-set-arrays(1)
