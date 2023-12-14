# This specfile is licensed under:
#
# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT
# License text: https://spdx.org/licenses/MIT.html

%bcond bootstrap 0
%bcond tests %{without bootstrap}
%if %{with tests} && %{with bootstrap}
%{error:--with tests and --with bootstrap are mutually exclusive}
%endif

Name:           tomcli
Version:        0.4.0
Release:        1%{?dist}
Summary:        CLI for working with TOML files. Pronounced "tom clee."

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
tomcli is a CLI for working with TOML files. Pronounced "tom clee."


%prep
%autosetup -p1


%generate_buildrequires
%{pyproject_buildrequires %{shrink:
    %{!?with_bootstrap:-x all,tomlkit,tomli}
    %{?with_tests:-x test}
}}


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files tomcli

mkdir -p %{buildroot}%{bash_completions_dir}
mkdir -p %{buildroot}%{fish_completions_dir}
mkdir -p %{buildroot}%{zsh_completions_dir}

(
export %{py3_test_envvars}
%{python3} compgen.py \
    --installroot %{buildroot} \
    --bash-dir %{bash_completions_dir} \
    --fish-dir %{fish_completions_dir} \
    --zsh-dir %{zsh_completions_dir}
)


%check
%if %{with tests}
%pytest
%endif


%pyproject_extras_subpkg -n tomcli all tomli tomlkit


%files -f %{pyproject_files}
%license LICENSES/*.txt
%doc README.md
%doc NEWS.md
%{_bindir}/tomcli*
%{bash_completions_dir}/tomcli*
%{fish_completions_dir}/tomcli*.fish
%{zsh_completions_dir}/_tomcli*


%changelog
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
