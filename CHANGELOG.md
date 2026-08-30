# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-29

### Added

- Bootstrap the repository from a local copy of the agent, command, and skill configuration.
- Add build and plan orchestrator agents.
- Add a global installer (`install.sh`) with update, uninstall, and dry-run support.
- Add Python, TypeScript, and bare-bones skills.
- Enable the bare-bones skill by default with a toggle to disable it.
- Add CONTRIBUTING.md with a contributor guide.
- Add README sections for prerequisites, what is included, CI status badge, security-conscious install, and local development.
- Apply comprehensive repository best-practices improvements.

### Changed

- Switch the developer-fast agent model to deepseek-v4-flash.
- Use valid opencode model IDs.

### Fixed

- Replace the broken shellcheck CI action with a native run step.
- Resolve shellcheck findings in `install.sh` and `setup-hooks.sh`.
- Use `BATS_TEST_DIRNAME` instead of a hardcoded path in `install.bats`.
- Change to a temporary directory in INST-01 so the clone path is exercised.
- Quote the bare-bones description for valid YAML parsing.

[1.0.0]: https://github.com/erikhoward/agent-tools/commits/v1.0.0
