# This specfile is licensed under:
#
# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT
# License text: https://spdx.org/licenses/MIT.html

# bconds:
#   tests
#       Run unit tests
#   tomlkit
#       Enable tomlkit and all extras
#   manpages
#       Build manpages using scdoc
#   bootstrap
#       Disable tomlkit dependencies and unit tests.
#       Add ~bootstrap to %%dist
#       Allows tomcli to be built early in the new Python bootstrap process.

%bcond bootstrap 0
%bcond tomlkit %{without bootstrap}
%bcond tests %{without bootstrap}
%bcond manpages 1

# Add minimal py3_test_envvars for EPEL 9
%if %{undefined py3_test_envvars}
%define py3_test_envvars %{shrink:
PYTHONPATH=%{buildroot}%{python3_sitelib}
PATH=%{buildroot}%{_bindir}:${PATH}
}
%endif

Name:           tomcli
Version:        0.6.0
Release:        1%{?dist}
Summary:        CLI for working with TOML files. Pronounced "tom clee."

License:        MIT
URL:            https://sr.ht/~gotmax23/tomcli
%global furl    https://git.sr.ht/~gotmax23/tomcli
Source0:        %{furl}/refs/download/v%{version}/tomcli-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  gnupg2
BuildRequires:  python3-devel
%if %{with manpages}
BuildRequires:  scdoc
%endif

# One of the TOML backends is required
Requires:       (%{py3_dist tomcli[tomlkit]} or %{py3_dist tomcli[tomli]})
%if %{with tomlkit}
# Prefer the tomlkit backend
Suggests:       %{py3_dist tomcli[tomlkit]}
# Recommend the 'all' extra
Recommends:     %{py3_dist tomcli[all]}
%endif


%description
tomcli is a CLI for working with TOML files. Pronounced "tom clee."


%prep
%autosetup -p1


%generate_buildrequires
%{pyproject_buildrequires %{shrink:
    -x tomli
    %{?with_tomlkit:-x all,tomlkit}
    %{?with_tests:-x test}
}}


%build
%pyproject_wheel

%if %{with manpages}
for page in doc/*.scd; do
    dest="${page%.scd}"
    scdoc <"${page}" >"${dest}"
done
%endif


%install
%pyproject_install
%pyproject_save_files tomcli

# Install manpages
install -Dpm 0644 doc/*.1 -t %{buildroot}%{_mandir}/man1

# Install shell completions
(
export %{py3_test_envvars}
%{python3} compgen.py \
    --installroot %{buildroot} \
    --bash-dir %{bash_completions_dir} \
    --fish-dir %{fish_completions_dir} \
    --zsh-dir %{zsh_completions_dir}
)


%check
# Smoke test
(
export %{py3_test_envvars}
TOMCLI="%{buildroot}%{_bindir}/tomcli"
cp pyproject.toml test.toml
name="$($TOMCLI get test.toml project.name)"
test "${name}" = "tomcli"

$TOMCLI set test.toml str project.name not-tomcli
newname="$($TOMCLI get test.toml project.name)"
test "${newname}" = "not-tomcli"
)

%pyproject_check_import
%if %{with tests}
%pytest
%endif


%pyproject_extras_subpkg -n tomcli %{?with_tomlkit:all tomlkit} tomli


%files -f %{pyproject_files}
%license LICENSE
%doc README.md
%doc NEWS.md
%{_bindir}/tomcli*
%{bash_completions_dir}/tomcli*
%{fish_completions_dir}/tomcli*.fish
%{zsh_completions_dir}/_tomcli*
%{_mandir}/man1/tomcli*.1*


%changelog
* Thu Mar 28 2024 Maxwell G <maxwell@gtmx.me> - 0.6.0-1
- Release 0.6.0.

* Thu Dec 14 2023 Maxwell G <maxwell@gtmx.me> - 0.5.0-1
- Release 0.5.0.

* Sat Dec 02 2023 Maxwell G <maxwell@gtmx.me> - 0.4.0-1
- Release 0.4.0.

* Thu Sep 07 2023 Maxwell G <maxwell@gtmx.me> - 0.3.0-1
- Release 0.3.0.

* Fri Sep 01 2023 Maxwell G <maxwell@gtmx.me> - 0.2.0-1
- Release 0.2.0.

* Sat May 20 2023 Maxwell G <maxwell@gtmx.me> - 0.1.2-1
- Release 0.1.2.

* Wed May 03 2023 Maxwell G <maxwell@gtmx.me> - 0.1.1-1
- Release 0.1.1.

* Fri Apr 14 2023 Maxwell G <maxwell@gtmx.me> - 0.1.0-1
- Release 0.1.0.

* Thu Apr 13 2023 Maxwell G <maxwell@gtmx.me> - 0.0.0-1
- Initial package
