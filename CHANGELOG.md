# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2023-03-14]

### Added

- Users can now create multiple machines at once with the scenario files
- Added a new component - `lateral_movement_ssh` to the Linux components, and its scenario
- Added Arguments for vulnerabilities

### Changed

- Changed how baseboxes are used. Vagrantfile for each basebox no longer exists. Instead, the ids to pull baseboxes is listed in `vm_box_list.ini`.
- Changed how error is raised, preserving the whole traceback

### Removed

- Removed extra functions

## [2023-02-08]

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