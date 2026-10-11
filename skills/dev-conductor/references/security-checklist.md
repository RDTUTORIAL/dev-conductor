# Security checklist

Read this when the task touches: authentication, authorization or permissions, user-controlled
input, file uploads, payments, secrets or tokens, PII, external APIs, webhooks, database trust
boundaries, serialization, shell or dynamic code execution, cryptography, sessions, or when
the system being built is itself an AI agent.

Skip it for everything else. Use `security-review` or framework-specific security skills too,
if installed, but this list is the baseline.

## Input and trust boundaries
- Validate all external input on the server, at the boundary where it enters. Client-side
  validation is UX only.
- Check for injection: SQL, command, template, path traversal, header, log.
- Treat deserialized data, webhook payloads, and third-party API responses as untrusted.
- Verify webhook signatures; make handlers idempotent.

## Authentication and authorization
- Every protected action checks authorization on the server, per request.
- Check object-level access (insecure direct object reference): does this user own this record?
- Look for privilege escalation paths: role fields settable by the client, missing checks on
  secondary endpoints, admin routes reachable without the admin check.
- Sessions and tokens: sensible expiry, secure cookie flags, no tokens in URLs or logs.

## Secrets and data exposure
- No secrets in code, config checked into git, logs, error messages, or client bundles.
- Responses return only the fields the caller needs; do not serialize internal models.
- Error messages do not leak stack traces, queries, or internal paths.
- PII is collected, stored, and logged only as needed.

## Unsafe defaults
- No permissive CORS, disabled TLS verification, or debug flags enabled outside local dev.
- File uploads: check type and size, store outside the web root, never execute them.
- Shell or dynamic execution: avoid it; if unavoidable, no user input reaches it unescaped.
- Cryptography: use the platform's vetted primitives; no homemade schemes.

## Dependencies
- Added dependencies are necessary, maintained, and not known-vulnerable.

## If the system is itself an AI agent or LLM app
- Prompt injection, direct and indirect (through tool output, web pages, documents).
- Tool permissions: least privilege; no tool broader than the task needs.
- Excessive agency: side effects with real cost (send, delete, pay, deploy) need a
  confirmation boundary.
- Data exfiltration paths: can untrusted content cause the agent to send private data out?
- Credentials: the agent never sees secrets it does not need.

## Reporting
State what was reviewed, what was found, and what was fixed. Do not mark security-sensitive
work complete without this step. If something could not be checked, say so.
