# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT

outdir ::= results_tomcli

srpm:
	command -v pipx || $(sudo) dnf install -y pipx
	command -v git || $(sudo) dnf install -y git-core
	pipx run nox -e srpm -- -o $(outdir)
