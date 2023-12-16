TOMCLI(1)

# NAME

*tomcli* -- CLI for working with TOML files. Pronounced "tom clee."

# SYNOPSIS

*tomcli* SUBCOMMAND [...]

*tomcli* --help

# DESCRIPTION

*tomcli* is a parent for the other subcommands

# COMMANDS

## get

The *tomcli-get* subcommand supports querying TOML files.
See tomcli-get(1) for more information.

```
tomcli get [OPTIONS] PATH [SELECTOR]
```

## formatters

The tomcli-formatters subcommand lists formatters available for use with
tomcli-get(1).
See tomcli-formatters(1) for more information.

```
tomcli formatters [OPTIONS]
```

## set

The *tomcli-set* subcommand supports modifying TOML files.
See tomcli-set(1) for more information.

```
tomcli set [GLOBAL OPTIONS] PATH COMMAND [OPTIONS] [ARGUMENTS]
```

## set lists

The *tomcli-set lists* subcommand supports modifying lists in TOML files.
See tomcli-set-lists(1) for more information.

```
tomcli set [GLOBAL OPTIONS] PATH lists COMMAND [ARGUMENTS]
tomcli set ... lists [COMMAND] --help
```
