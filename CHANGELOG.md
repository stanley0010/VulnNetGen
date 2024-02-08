# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2023-02-08] - Stanley Chan

### Added

- a Changelog file
- Linux component - wordpress with weak admin password, and a scenario file for it 
- time count for creating machine of a scenario


### Changed

- Changed playbook template such that each component's `main.yaml` is a complete playbook instead of just "tasks"
- Fixed the excessive privilege level(root) to run certain tasks in different components
- each vm will be provisioned with a unique name now, avoiding vm name conflicts

### Removed

- Trademark sign previously shown after the project description in version 
0.3.0