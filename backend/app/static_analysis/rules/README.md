# Offline Semgrep rules

Community rule-pack snapshots were downloaded from `https://semgrep.dev/c/p/<pack>`
on 2026-10-01 using Semgrep CLI version 1.176.0. The Registry endpoints returned
JSON rule configurations, which were serialized as ASCII-safe YAML for Windows
compatibility.

| Pack | Registry rule count |
|---|---:|
| `ci.yaml` (`p/ci`) | 160 |
| `owasp-top-ten.yaml` (`p/owasp-top-ten`) | 560 |
| `security-audit.yaml` (`p/security-audit`) | 225 |
| `javascript.yaml` (`p/javascript`) | 74 |
| `java.yaml` (`p/java`) | 60 |
| `c.yaml` (`p/c`) | 2 |

The runner uses the committed, deduplicated per-language YAML snapshots
(`python.yaml`, `javascript.yaml`, `java.yaml`, `c.yaml`, and `cpp.yaml`) so
Semgrep does not parse unrelated languages or duplicate rule IDs on each scan.
The source snapshots above retain the complete downloaded packs. Regenerate the
per-language files only from those snapshots; runtime scans make no Registry
requests.

These rules are distributed under the Semgrep Rules License v1.0. See
https://semgrep.dev/legal/rules-license.
