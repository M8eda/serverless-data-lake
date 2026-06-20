
# Security Policy | Vulnerability Disclosure Guidelines

We place a high priority on the security of our data engineering solutions and infrastructure templates. If you suspect or discover a potential security flaw, vulnerability, or exposure within this architecture, please report it immediately through professional communication channels.

## Reporting a Security Issue

**Please do not create public GitHub issues or forum discussions for tracking potential security vulnerabilities.** Instead, submit all details safely via the official corporate or provider-specific vulnerability reporting workflows:

* **Enterprise Reporting Portal**: Route your detailed security observations through your designated organizational internal tracking platform or primary cloud provider security center.
* **Email Communication**: Forward structured write-ups directly to the specialized security response desks or drop a formal message to ws-security@amazon.com for underlying core cloud platform framework compromises.

To help our engineering triage teams inspect your findings efficiently, please include a comprehensive summary containing:

1. A descriptive overview of the suspected vulnerability behavior.
2. Exact file paths or infrastructural components affected (e.g., source/lambdas/firehose_transform.py or deployment/lakeformation_stack.py).
3. Clear step-by-step reproduction instructions or mockup payloads to illustrate potential exploit tracks.

## Security Practices for Local Customizations

When configuring or deploying your customized instance of this Serverless Data Lake, ensure your team follows cloud engineering best practices:

* **Secrets Management**: Never commit hardcoded API keys, database credentials, or plain text IAM secret access lines inside your environment files (.env) or Python source code scripts. Always connect stacks dynamically to Secrets Manager structures.
* **Least Privilege Mapping**: Periodically audit your lakeformation_stack.py and quicksight_stack.py configurations to ensure active consumer groups are only granted access to the specific database columns required for business operational routines.
