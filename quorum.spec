Name:		quorum
Version:	2
Release:	1%{?dist}
Summary:	Privileged command execution via quorum voting.

Group:		SEAS
License:	BSD
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:	python
Requires:	python

%description
%{summary}

%prep
%setup -q


%build
python setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python setup.py install --root=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc



%changelog
