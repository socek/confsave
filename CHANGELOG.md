# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning]
(http://semver.org/).

## 0.3.0 - [Unreleased]
### Fixed
- Add will not allow to add paths from outside of user's folder

## 0.2.0 - 2017-06-02
### Added
- Application.Settings can be changed by the command line interface
- Populate Command which allow to populate configs from the repo.

### Changed
- Commit command without remote repo set will not break the command. It will just commit without pushing it.
- Commit command is now adding all changes to the commit.
- Add Command can now add folders to the repo.

## 0.1.0 - 2017-05-06
### Added
- Command line interface
- Add file
- Status of tracked files
- List of untracked files
- Set external repo
- This CHANGELOG file to hopefully serve as an evolving example of a standardized open source project CHANGELOG.
