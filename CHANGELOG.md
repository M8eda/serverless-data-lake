# Changelog: Serverless Data Lake

All notable changes to this project will be documented in this file.

## [v9.0] - 2026-06-20
### Added
- Finalized Athena workgroup enforcement.
- Added explicit removal policies for dev/test environments (using RemovalPolicy.DESTROY).
- Refined app context handling and dependency ordering for cross-stack stability.

## [v8.0] - 2026-06-20
### Added
- Dedicated S3 bucket for Glue scripts to improve security/lifecycle control.
- Explicit Glue worker configuration (type and count).
- Added QuickSight permissions and exposed Glue role ARN for Lake Formation.
- Improved dependency management between S3, Kinesis, Glue, Athena, and QuickSight.

## [v7.0] - 2026-06-19
### Changed
- Continued cleanup and consistency fixes across deployment stacks.
- Minor refactoring and added documentation comments.

## [v6.0] - 2026-06-19
### Changed
- Added clearer stack dependencies (dd_dependency) to prevent deployment race conditions.
- Added clearer outputs for Athena and Glue stacks.

## [v5.0] - 2026-06-19
### Changed
- Adjusted CDK stack and lambda asset paths to align with the repository layout.
- Fixed handler folder names and deployment targets.

## [v4.0] - 2026-06-19
### Added
- Reintroduced realistic Glue job logic using PySpark and GlueContext.
- Added schema normalization (lowercase columns) and data casting (DecimalType).
- Implemented core transformation and aggregation logic.

## [v3.0] - 2026-06-19
### Added
- Initial implementation of testable Python stubs for Glue and Lambda.
- Added pytest suite for rapid feedback loops without needing Spark runtime.

## [v2.0] - 2026-06-19
### Added
- Initial baseline project structure and Git initialization.
- Basic infrastructure skeleton for Raw/Curated zones.
