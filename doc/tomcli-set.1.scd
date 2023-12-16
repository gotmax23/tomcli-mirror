TOMCLI-SET(1)

# NAME

tomcli-set -- CLI for working with TOML files. Pronounced "tom clee."

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
	Example: 'section1.subsection.value' or '"key.with.dots".abc'

# GLOBAL OPTIONS

*--version*
	Show the version and exit.
*--writer* <tomli_w|tomlkit>
	Library to use to write TOML files.
*--reader* <tomli|tomlkit>
	Library to use to write TOML files.
	Defaults to tomlkit and falls back to tomli/tomllib if tomlkit is unavailable.

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
tomcli-set [GLOBAL OPTIONS] PATH del SELECTOR [OPTIONS]
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
tomcli-set [GLOBAL OPTIONS] PATH [str|int|float] [OPTIONS] SELECTOR
tomcli-set ... [str|int|float] --help
```

## lists

Subcommand to modify TOML lists. See tomcli-set-lists(1).


# SEE ALSO

tomcli(1), tomcli-formatters(1), tomcli-get(1), tomcli-set-lists(1)
