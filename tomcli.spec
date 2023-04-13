Name:           tomcli
Version:        0.0.0
Release:        1%{?dist}
Summary:        CLI for working with TOML files. Pronounced "tohm-clee."

License:        MIT
URL:            https://sr.ht/~gotmax23/tomcli
%global furl    https://git.sr.ht/~gotmax23/tomcli
Source0:        %{furl}/refs/download/v%{version}/tomcli-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  %{py3_dist pytest}

Requires:       (%{py3_dist tomcli[tomlkit]} or %{py3_dist tomcli[tomli]})
Suggests:       %{py3_dist tomcli[tomlkit]}
Recommends:     %{py3_dist tomcli[all]}


%description
tomcli is a CLI for working with TOML files. Pronounced "tohm-clee."


%prep
%autosetup -p1 -n tomcli-%{version}


%generate_buildrequires
%pyproject_buildrequires -x all,tomlkit,tomli,test


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files tomcli


%check
%pytest


%files -f %{pyproject_files}
%license LICENSES/*.txt
%doc README.md
%{_bindir}/tomcli*


%changelog
* Thu Apr 13 2023 Maxwell G <maxwell@gtmx.me> - 0.0.0-1
- Initial package
