# This specfile is licensed under:
#
# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT
# License text: https://spdx.org/licenses/MIT.html

Name:           tomcli
Version:        0.1.0
Release:        1%{?dist}
Summary:        CLI for working with TOML files. Pronounced "tohm-clee."

License:        MIT
URL:            https://sr.ht/~gotmax23/tomcli
%global furl    https://git.sr.ht/~gotmax23/tomcli
Source0:        %{furl}/refs/download/v%{version}/tomcli-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  gnupg2
BuildRequires:  python3-devel
BuildRequires:  %{py3_dist pytest}

# One of the TOML backends is required
Requires:       (%{py3_dist tomcli[tomlkit]} or %{py3_dist tomcli[tomli]})
# Prefer the tomlkit backend
Suggests:       %{py3_dist tomcli[tomlkit]}
# Recommend the 'all' extra
Recommends:     %{py3_dist tomcli[all]}


%description
tomcli is a CLI for working with TOML files. Pronounced "tohm-clee."


%prep
%autosetup -p1


%generate_buildrequires
%pyproject_buildrequires -x all,tomlkit,tomli,test


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files tomcli

mkdir -p %{buildroot}%{bash_completions_dir}
mkdir -p %{buildroot}%{fish_completions_dir}
mkdir -p %{buildroot}%{zsh_completions_dir}

(
export PYTHONPATH="%{buildroot}%{python3_sitelib}"
export _TYPER_COMPLETE_TEST_DISABLE_SHELL_DETECTION=1
for command in %{buildroot}%{_bindir}/tomcli*; do
    $command --show-completion=bash > "%{buildroot}%{bash_completions_dir}/$(basename $command)"
    $command --show-completion=fish > "%{buildroot}%{fish_completions_dir}/$(basename $command).fish"
    $command --show-completion=zsh > "%{buildroot}%{zsh_completions_dir}/_$(basename $command)"
done
)


%check
%pytest


%pyproject_extras_subpkg -n tomcli all tomli tomlkit


%files -f %{pyproject_files}
# I prefer not to rely on %%pyproject_save_files to mark files with %%license.
# Also, Fedora's hatchling supports the current draft of PEP 639, but EPEL 9's
# does not.
%license LICENSES/*.txt
%doc README.md
%doc NEWS.md
%{_bindir}/tomcli*
%{bash_completions_dir}/tomcli*
%{fish_completions_dir}/tomcli*.fish
%{zsh_completions_dir}/_tomcli*


%changelog
* Fri Apr 14 2023 Maxwell G <maxwell@gtmx.me> - 0.1.0-1
- Release 0.1.0.

* Thu Apr 13 2023 Maxwell G <maxwell@gtmx.me> - 0.0.0-1
- Initial package
