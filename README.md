<!--
Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
SPDX-License-Identifier: MIT
-->

# [tomcli](https://tomcli.gtmx.me)

[![builds.sr.ht status](https://builds.sr.ht/~gotmax23/tomcli/commits/main.svg)](https://builds.sr.ht/~gotmax23/tomcli/commits/main?)

[![copr build status][badge-copr]][link-copr] (gotmax23/tomcli)

[![copr build status][badge-copr-dev]][link-copr-dev] (gotmax23/tomcli-dev)

CLI for working with TOML files. Pronounced "tom clee."

## Links

- [**tomcli docsite**](https://tomcli.gtmx.me)
- [tomcli project hub](https://sr.ht/~gotmax23/tomcli)
- [tomcli git.sr.ht repo](https://git.sr.ht/~gotmax23/tomcli)
- [tomcli tracker](https://todo.sr.ht/~gotmax23/tomcli)
- [tomcli mailing list][archives] ([~gotmax/tomcli@lists.sr.ht][mailto])

[archives]: https://lists.sr.ht/~gotmax23/tomcli
[mailto]: mailto:~gotmax/tomcli@lists.sr.ht

## Examples

### `tomcli-get`

> Query TOML files

Print a TOML table:

``` console
$ tomcli-get pyproject.toml build-system
[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"
```

Get a newline-separated list of strings:

``` console
$ tomcli-get pyproject.toml --formatter newline-list project.dependencies
click
importlib_metadata; python_version<'3.11'
```

List all available formatters for use
with `tomcli-get -F` / `tomcli-get --formatter`:

``` console
$ tomcli-formatters
default
	Use the `toml` formatter if the object is a Mapping and fall back to
	`string`.

json
	Return the JSON representation of the object

newline-list
	Return a newline separated list

string
	Print the Python str() representation of the object

toml
	Return the TOML mapping of the object

```

### `tomcli-set`

> Modify TOML files

Delete a TOML value:

``` console
$ tomcli-set pyproject.toml del 'project.dependencies'
```

Set a value to `true` or `false`:

``` console
$ tomcli-set pyproject.toml true 'tool.mypy.check_untyped_defs'
$ tomcli-set pyproject.toml false 'tool.mypy.check_untyped_defs'
```

Set a `float` or `int` value:

``` console
$ tomcli-set pyproject.toml float 'tool.coverage.run.fail_under' '90.0'
$ tomcli-set pyproject.toml int 'tool.coverage.run.fail_under' '90'
```

Set a string value:

``` console
$ tomcli-set pyproject.toml str 'project.readme' 'README.rst'
```

### `tomcli-get lists`

> Modify lists within a TOML file

Remove all values that match a Python regex:

> **NOTE:** The regex must match the entire string

``` console
$ tomcli-set pyproject.toml lists delitem \
    'project.classifiers' 'Programming Language :: Python.*'
```

Remove all values that match an fnmatch-style pattern:

``` console
$ tomcli-set pyproject.toml lists delitem --type fnmatch \
    'project.optional-dependencies.dev' '*cov*'
```

Replace values that match a Python regex:

> **NOTE:** The regex must match the entire string

``` console
$ tomcli-set pyproject.toml lists replace \
    'project.optional-dependencies.test' '(.+)==(.+)' '\1>=\2'
```

Create a list of strings:

``` console
## Create the new file
$ touch plays.toml
## Automatically creates the "Romeo and Juliet" table
$ tomcli-set plays.toml lists str \
    '"Romeo and Juliet".characters' 'Romeo' 'Juliet' 'Mercuitio' 'Nurse'
```


## Contributing

See [CONTRIBUTING.md](https://git.sr.ht/~gotmax23/tomcli/tree/main/item/CONTRIBUTING.md).

## License

This repository is licensed under

    SPDX-License-Identifer: MIT

[badge-copr]: https://copr.fedorainfracloud.org/coprs/gotmax23/tomcli/package/tomcli/status_image/last_build.png
[link-copr]: https://copr.fedorainfracloud.org/coprs/gotmax23/tomcli/
[badge-copr-dev]: https://copr.fedorainfracloud.org/coprs/gotmax23/tomcli-dev/package/tomcli/status_image/last_build.png
[link-copr-dev]: https://copr.fedorainfracloud.org/coprs/gotmax23/tomcli-dev/
