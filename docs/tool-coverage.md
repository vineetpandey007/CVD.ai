# Static-analysis tool coverage

The non-Semgrep tools were measured on 2026-10-01 with Bandit 1.9.4, Ruff 0.16.6, Flawfinder 2.0.20, Cppcheck 2.17.1 (cppcheck-wheel 1.5.1), and njsscan 1.0.1. Semgrep 1.172.0 and its custom rules were rerun on 2026-10-02. Applicable runners were called directly (not through the API); njsscan was additionally examined as a raw CLI because its Windows backend silently skips semantic analysis. Semgrep used one batch scan per language; its elapsed time is shared by the files in that batch and shown in the evidence table.

## Raw finding counts

| Fixture | Language | Expected | CWE | Bandit | Ruff | Semgrep | Flawfinder | Cppcheck | njsscan |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| vulnerable_samples/120_c.c | c | vulnerable | CWE-120 | N/A | N/A | 1 | 2 | 1 | N/A |
| vulnerable_samples/120_cpp.cpp | cpp | vulnerable | CWE-120 | N/A | N/A | 0 | 2 | 0 | N/A |
| vulnerable_samples/22_c.c | c | vulnerable | CWE-22 | N/A | N/A | 1 | 3 | 4 | N/A |
| vulnerable_samples/22_cpp.cpp | cpp | vulnerable | CWE-22 | N/A | N/A | 1 | 0 | 0 | N/A |
| vulnerable_samples/22_java.java | java | vulnerable | CWE-22 | N/A | N/A | 1 | N/A | N/A | N/A |
| vulnerable_samples/22_javascript.js | javascript | vulnerable | CWE-22 | N/A | N/A | 1 | N/A | N/A | UNSUPPORTED |
| vulnerable_samples/22_python.py | python | vulnerable | CWE-22 | 0 | 0 | 1 | N/A | N/A | N/A |
| vulnerable_samples/502_cpp.cpp | cpp | vulnerable | CWE-502 | N/A | N/A | 0 | 0 | 0 | N/A |
| vulnerable_samples/502_java.java | java | vulnerable | CWE-502 | N/A | N/A | 1 | N/A | N/A | N/A |
| vulnerable_samples/502_javascript.js | javascript | vulnerable | CWE-502 | N/A | N/A | 0 | N/A | N/A | UNSUPPORTED |
| vulnerable_samples/502_python.py | python | vulnerable | CWE-502 | 2 | 1 | 1 | N/A | N/A | N/A |
| vulnerable_samples/78_c.c | c | vulnerable | CWE-78 | N/A | N/A | 0 | 3 | 1 | N/A |
| vulnerable_samples/78_cpp.cpp | cpp | vulnerable | CWE-78 | N/A | N/A | 0 | 1 | 0 | N/A |
| vulnerable_samples/78_java.java | java | vulnerable | CWE-78 | N/A | N/A | 0 | N/A | N/A | N/A |
| vulnerable_samples/78_javascript.js | javascript | vulnerable | CWE-78 | N/A | N/A | 2 | N/A | N/A | UNSUPPORTED |
| vulnerable_samples/78_python.py | python | vulnerable | CWE-78 | 1 | 1 | 0 | N/A | N/A | N/A |
| vulnerable_samples/79_c.c | c | vulnerable | CWE-79 | N/A | N/A | 0 | 1 | 1 | N/A |
| vulnerable_samples/79_cpp.cpp | cpp | vulnerable | CWE-79 | N/A | N/A | 0 | 0 | 0 | N/A |
| vulnerable_samples/79_java.java | java | vulnerable | CWE-79 | N/A | N/A | 1 | N/A | N/A | N/A |
| vulnerable_samples/79_javascript.js | javascript | vulnerable | CWE-79 | N/A | N/A | 1 | N/A | N/A | UNSUPPORTED |
| vulnerable_samples/79_python.py | python | vulnerable | CWE-79 | 0 | 0 | 2 | N/A | N/A | N/A |
| vulnerable_samples/89_c.c | c | vulnerable | CWE-89 | N/A | N/A | 0 | 2 | 1 | N/A |
| vulnerable_samples/89_cpp.cpp | cpp | vulnerable | CWE-89 | N/A | N/A | 0 | 0 | 0 | N/A |
| vulnerable_samples/89_java.java | java | vulnerable | CWE-89 | N/A | N/A | 2 | N/A | N/A | N/A |
| vulnerable_samples/89_javascript.js | javascript | vulnerable | CWE-89 | N/A | N/A | 1 | N/A | N/A | UNSUPPORTED |
| vulnerable_samples/89_python.py | python | vulnerable | CWE-89 | 1 | 1 | 0 | N/A | N/A | N/A |
| safe_samples/120_c.c | c | safe | CWE-120 | N/A | N/A | 0 | 2 | 1 | N/A |
| safe_samples/120_cpp.cpp | cpp | safe | CWE-120 | N/A | N/A | 0 | 1 | 0 | N/A |
| safe_samples/22_c.c | c | safe | CWE-22 | N/A | N/A | 0 | 4 | 2 | N/A |
| safe_samples/22_cpp.cpp | cpp | safe | CWE-22 | N/A | N/A | 0 | 0 | 0 | N/A |
| safe_samples/22_java.java | java | safe | CWE-22 | N/A | N/A | 0 | N/A | N/A | N/A |
| safe_samples/22_javascript.js | javascript | safe | CWE-22 | N/A | N/A | 0 | N/A | N/A | UNSUPPORTED |
| safe_samples/22_python.py | python | safe | CWE-22 | 0 | 0 | 0 | N/A | N/A | N/A |
| safe_samples/502_cpp.cpp | cpp | safe | CWE-502 | N/A | N/A | 0 | 0 | 0 | N/A |
| safe_samples/502_java.java | java | safe | CWE-502 | N/A | N/A | 0 | N/A | N/A | N/A |
| safe_samples/502_javascript.js | javascript | safe | CWE-502 | N/A | N/A | 0 | N/A | N/A | UNSUPPORTED |
| safe_samples/502_python.py | python | safe | CWE-502 | 0 | 0 | 0 | N/A | N/A | N/A |
| safe_samples/78_c.c | c | safe | CWE-78 | N/A | N/A | 0 | 1 | 0 | N/A |
| safe_samples/78_cpp.cpp | cpp | safe | CWE-78 | N/A | N/A | 0 | 1 | 0 | N/A |
| safe_samples/78_java.java | java | safe | CWE-78 | N/A | N/A | 0 | N/A | N/A | N/A |
| safe_samples/78_javascript.js | javascript | safe | CWE-78 | N/A | N/A | 0 | N/A | N/A | UNSUPPORTED |
| safe_samples/78_python.py | python | safe | CWE-78 | 3 | 2 | 0 | N/A | N/A | N/A |
| safe_samples/79_c.c | c | safe | CWE-79 | N/A | N/A | 0 | 1 | 0 | N/A |
| safe_samples/79_cpp.cpp | cpp | safe | CWE-79 | N/A | N/A | 0 | 0 | 0 | N/A |
| safe_samples/79_java.java | java | safe | CWE-79 | N/A | N/A | 0 | N/A | N/A | N/A |
| safe_samples/79_javascript.js | javascript | safe | CWE-79 | N/A | N/A | 0 | N/A | N/A | UNSUPPORTED |
| safe_samples/79_python.py | python | safe | CWE-79 | 0 | 0 | 2 | N/A | N/A | N/A |
| safe_samples/89_c.c | c | safe | CWE-89 | N/A | N/A | 0 | 0 | 0 | N/A |
| safe_samples/89_cpp.cpp | cpp | safe | CWE-89 | N/A | N/A | 0 | 0 | 0 | N/A |
| safe_samples/89_java.java | java | safe | CWE-89 | N/A | N/A | 0 | N/A | N/A | N/A |
| safe_samples/89_javascript.js | javascript | safe | CWE-89 | N/A | N/A | 0 | N/A | N/A | UNSUPPORTED |
| safe_samples/89_python.py | python | safe | CWE-89 | 0 | 0 | 0 | N/A | N/A | N/A |

## Vulnerable language/CWE coverage (exact CWE mapping)

A pair counts as detected only when a vulnerable fixture produced at least one finding mapped to that exact CWE. A generic finding count is not treated as CWE coverage.

| Language | CWE | Detecting tool(s) | Status |
|---|---|---|---|
| c | CWE-120 | flawfinder | flawfinder |
| c | CWE-22 | semgrep | semgrep |
| c | CWE-78 | flawfinder | flawfinder |
| c | CWE-79 | — | NO TOOL DETECTED |
| c | CWE-89 | — | NO TOOL DETECTED |
| cpp | CWE-120 | flawfinder | flawfinder |
| cpp | CWE-22 | semgrep | semgrep |
| cpp | CWE-502 | — | NO TOOL DETECTED |
| cpp | CWE-78 | flawfinder | flawfinder |
| cpp | CWE-79 | — | NO TOOL DETECTED |
| cpp | CWE-89 | — | NO TOOL DETECTED |
| java | CWE-22 | semgrep | semgrep |
| java | CWE-502 | semgrep | semgrep |
| java | CWE-78 | — | NO TOOL DETECTED |
| java | CWE-79 | semgrep | semgrep |
| java | CWE-89 | semgrep | semgrep |
| javascript | CWE-22 | semgrep | semgrep |
| javascript | CWE-502 | — | NO TOOL DETECTED |
| javascript | CWE-78 | semgrep | semgrep |
| javascript | CWE-79 | semgrep | semgrep |
| javascript | CWE-89 | semgrep | semgrep |
| python | CWE-22 | semgrep | semgrep |
| python | CWE-502 | bandit, ruff, semgrep | bandit, ruff, semgrep |
| python | CWE-78 | bandit, ruff | bandit, ruff |
| python | CWE-79 | semgrep | semgrep |
| python | CWE-89 | bandit, ruff | bandit, ruff |

## Coverage before and after custom rules

The previously recorded matrix had 9 vulnerable language/CWE pairs with exact mapped detections. The post-change matrix has 19. The earlier test harness appended the source suffix a second time when looking up Semgrep batch results (for example, `.java.java`), so it discarded batch findings. The 10 newly recorded pairs below include detections from the new custom rules and existing offline rules that the corrected batch lookup now retains.

- `c` CWE-22
- `cpp` CWE-22
- `java` CWE-22
- `java` CWE-502
- `java` CWE-79
- `javascript` CWE-22
- `javascript` CWE-79
- `javascript` CWE-89
- `python` CWE-22
- `python` CWE-79

The new custom rules were directly smoke-tested on vulnerable and safe path fixtures, the JavaScript HTML sink and SQL/command-concatenation fixtures, and an ad hoc `eval`-concatenation snippet. The safe path fixtures did not trigger these rules.

## Safe-fixture false positives

| Fixture | CWE | Tool | Findings | CWE IDs returned |
|---|---|---|---:|---|
| safe_samples/120_c.c | CWE-120 | flawfinder | 2 | CWE-120, CWE-134 |
| safe_samples/120_c.c | CWE-120 | cppcheck | 1 | CWE-398 |
| safe_samples/120_cpp.cpp | CWE-120 | flawfinder | 1 | CWE-120 |
| safe_samples/22_c.c | CWE-22 | flawfinder | 4 | CWE-120, CWE-134, CWE-362 |
| safe_samples/22_c.c | CWE-22 | cppcheck | 2 | CWE-398, CWE-771 |
| safe_samples/78_c.c | CWE-78 | flawfinder | 1 | CWE-78 |
| safe_samples/78_cpp.cpp | CWE-78 | flawfinder | 1 | CWE-78 |
| safe_samples/78_python.py | CWE-78 | bandit | 3 | CWE-78 |
| safe_samples/78_python.py | CWE-78 | ruff | 2 | CWE-78 |
| safe_samples/79_c.c | CWE-79 | flawfinder | 1 | CWE-134 |
| safe_samples/79_python.py | CWE-79 | semgrep | 2 | CWE-79 |

## Per-runner evidence

| Tool | Fixture | Language | Expected | Found | Finding CWEs | Elapsed seconds | Warning |
|---|---|---|---|---:|---|---:|---|
| semgrep | vulnerable_samples/120_c.c | c | vulnerable | 1 | CWE-676 | 29.283 (shared language batch) | none |
| flawfinder | vulnerable_samples/120_c.c | c | vulnerable | 2 | CWE-120 | 1.345 | none |
| cppcheck | vulnerable_samples/120_c.c | c | vulnerable | 1 | CWE-398 | 1.473 | none |
| semgrep | vulnerable_samples/120_cpp.cpp | cpp | vulnerable | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | vulnerable_samples/120_cpp.cpp | cpp | vulnerable | 2 | CWE-120 | 1.152 | none |
| cppcheck | vulnerable_samples/120_cpp.cpp | cpp | vulnerable | 0 | none | 1.554 | none |
| semgrep | vulnerable_samples/22_c.c | c | vulnerable | 1 | CWE-22 | 29.283 (shared language batch) | none |
| flawfinder | vulnerable_samples/22_c.c | c | vulnerable | 3 | CWE-120, CWE-362 | 0.979 | none |
| cppcheck | vulnerable_samples/22_c.c | c | vulnerable | 4 | CWE-398, CWE-563, CWE-775 | 1.237 | none |
| semgrep | vulnerable_samples/22_cpp.cpp | cpp | vulnerable | 1 | CWE-22 | 29.974 (shared language batch) | none |
| flawfinder | vulnerable_samples/22_cpp.cpp | cpp | vulnerable | 0 | none | 1.212 | none |
| cppcheck | vulnerable_samples/22_cpp.cpp | cpp | vulnerable | 0 | none | 1.421 | none |
| semgrep | vulnerable_samples/22_java.java | java | vulnerable | 1 | CWE-22 | 36.688 (shared language batch) | none |
| semgrep | vulnerable_samples/22_javascript.js | javascript | vulnerable | 1 | CWE-22 | 38.511 (shared language batch) | none |
| njsscan | vulnerable_samples/22_javascript.js | javascript | vulnerable | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | vulnerable_samples/22_python.py | python | vulnerable | 0 | none | 2.519 | none |
| ruff | vulnerable_samples/22_python.py | python | vulnerable | 0 | none | 0.212 | none |
| semgrep | vulnerable_samples/22_python.py | python | vulnerable | 1 | CWE-22 | 49.267 (shared language batch) | none |
| semgrep | vulnerable_samples/502_cpp.cpp | cpp | vulnerable | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | vulnerable_samples/502_cpp.cpp | cpp | vulnerable | 0 | none | 1.087 | none |
| cppcheck | vulnerable_samples/502_cpp.cpp | cpp | vulnerable | 0 | none | 1.436 | none |
| semgrep | vulnerable_samples/502_java.java | java | vulnerable | 1 | CWE-502 | 36.688 (shared language batch) | none |
| semgrep | vulnerable_samples/502_javascript.js | javascript | vulnerable | 0 | none | 38.511 (shared language batch) | none |
| njsscan | vulnerable_samples/502_javascript.js | javascript | vulnerable | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | vulnerable_samples/502_python.py | python | vulnerable | 2 | CWE-502 | 2.521 | none |
| ruff | vulnerable_samples/502_python.py | python | vulnerable | 1 | CWE-502 | 0.184 | none |
| semgrep | vulnerable_samples/502_python.py | python | vulnerable | 1 | CWE-502 | 49.267 (shared language batch) | none |
| semgrep | vulnerable_samples/78_c.c | c | vulnerable | 0 | none | 29.283 (shared language batch) | none |
| flawfinder | vulnerable_samples/78_c.c | c | vulnerable | 3 | CWE-120, CWE-78 | 0.939 | none |
| cppcheck | vulnerable_samples/78_c.c | c | vulnerable | 1 | CWE-398 | 1.383 | none |
| semgrep | vulnerable_samples/78_cpp.cpp | cpp | vulnerable | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | vulnerable_samples/78_cpp.cpp | cpp | vulnerable | 1 | CWE-78 | 1.117 | none |
| cppcheck | vulnerable_samples/78_cpp.cpp | cpp | vulnerable | 0 | none | 1.537 | none |
| semgrep | vulnerable_samples/78_java.java | java | vulnerable | 0 | none | 36.688 (shared language batch) | none |
| semgrep | vulnerable_samples/78_javascript.js | javascript | vulnerable | 2 | CWE-78 | 38.511 (shared language batch) | none |
| njsscan | vulnerable_samples/78_javascript.js | javascript | vulnerable | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | vulnerable_samples/78_python.py | python | vulnerable | 1 | CWE-78 | 2.635 | none |
| ruff | vulnerable_samples/78_python.py | python | vulnerable | 1 | CWE-78 | 0.274 | none |
| semgrep | vulnerable_samples/78_python.py | python | vulnerable | 0 | none | 49.267 (shared language batch) | none |
| semgrep | vulnerable_samples/79_c.c | c | vulnerable | 0 | none | 29.283 (shared language batch) | none |
| flawfinder | vulnerable_samples/79_c.c | c | vulnerable | 1 | CWE-134 | 1.114 | none |
| cppcheck | vulnerable_samples/79_c.c | c | vulnerable | 1 | CWE-398 | 1.440 | none |
| semgrep | vulnerable_samples/79_cpp.cpp | cpp | vulnerable | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | vulnerable_samples/79_cpp.cpp | cpp | vulnerable | 0 | none | 1.094 | none |
| cppcheck | vulnerable_samples/79_cpp.cpp | cpp | vulnerable | 0 | none | 1.295 | none |
| semgrep | vulnerable_samples/79_java.java | java | vulnerable | 1 | CWE-79 | 36.688 (shared language batch) | none |
| semgrep | vulnerable_samples/79_javascript.js | javascript | vulnerable | 1 | CWE-79 | 38.511 (shared language batch) | none |
| njsscan | vulnerable_samples/79_javascript.js | javascript | vulnerable | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | vulnerable_samples/79_python.py | python | vulnerable | 0 | none | 2.520 | none |
| ruff | vulnerable_samples/79_python.py | python | vulnerable | 0 | none | 0.276 | none |
| semgrep | vulnerable_samples/79_python.py | python | vulnerable | 2 | CWE-79 | 49.267 (shared language batch) | none |
| semgrep | vulnerable_samples/89_c.c | c | vulnerable | 0 | none | 29.283 (shared language batch) | none |
| flawfinder | vulnerable_samples/89_c.c | c | vulnerable | 2 | CWE-120 | 1.137 | none |
| cppcheck | vulnerable_samples/89_c.c | c | vulnerable | 1 | CWE-398 | 1.485 | none |
| semgrep | vulnerable_samples/89_cpp.cpp | cpp | vulnerable | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | vulnerable_samples/89_cpp.cpp | cpp | vulnerable | 0 | none | 1.072 | none |
| cppcheck | vulnerable_samples/89_cpp.cpp | cpp | vulnerable | 0 | none | 1.486 | none |
| semgrep | vulnerable_samples/89_java.java | java | vulnerable | 2 | CWE-89 | 36.688 (shared language batch) | none |
| semgrep | vulnerable_samples/89_javascript.js | javascript | vulnerable | 1 | CWE-89 | 38.511 (shared language batch) | none |
| njsscan | vulnerable_samples/89_javascript.js | javascript | vulnerable | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | vulnerable_samples/89_python.py | python | vulnerable | 1 | CWE-89 | 2.458 | none |
| ruff | vulnerable_samples/89_python.py | python | vulnerable | 1 | CWE-89 | 0.241 | none |
| semgrep | vulnerable_samples/89_python.py | python | vulnerable | 0 | none | 49.267 (shared language batch) | none |
| semgrep | safe_samples/120_c.c | c | safe | 0 | none | 29.283 (shared language batch) | none |
| flawfinder | safe_samples/120_c.c | c | safe | 2 | CWE-120, CWE-134 | 0.931 | none |
| cppcheck | safe_samples/120_c.c | c | safe | 1 | CWE-398 | 1.522 | none |
| semgrep | safe_samples/120_cpp.cpp | cpp | safe | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | safe_samples/120_cpp.cpp | cpp | safe | 1 | CWE-120 | 1.086 | none |
| cppcheck | safe_samples/120_cpp.cpp | cpp | safe | 0 | none | 1.477 | none |
| semgrep | safe_samples/22_c.c | c | safe | 0 | none | 29.283 (shared language batch) | none |
| flawfinder | safe_samples/22_c.c | c | safe | 4 | CWE-120, CWE-134, CWE-362 | 1.031 | none |
| cppcheck | safe_samples/22_c.c | c | safe | 2 | CWE-398, CWE-771 | 1.492 | none |
| semgrep | safe_samples/22_cpp.cpp | cpp | safe | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | safe_samples/22_cpp.cpp | cpp | safe | 0 | none | 0.951 | none |
| cppcheck | safe_samples/22_cpp.cpp | cpp | safe | 0 | none | 1.374 | none |
| semgrep | safe_samples/22_java.java | java | safe | 0 | none | 36.688 (shared language batch) | none |
| semgrep | safe_samples/22_javascript.js | javascript | safe | 0 | none | 38.511 (shared language batch) | none |
| njsscan | safe_samples/22_javascript.js | javascript | safe | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | safe_samples/22_python.py | python | safe | 0 | none | 2.697 | none |
| ruff | safe_samples/22_python.py | python | safe | 0 | none | 0.334 | none |
| semgrep | safe_samples/22_python.py | python | safe | 0 | none | 49.267 (shared language batch) | none |
| semgrep | safe_samples/502_cpp.cpp | cpp | safe | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | safe_samples/502_cpp.cpp | cpp | safe | 0 | none | 1.116 | none |
| cppcheck | safe_samples/502_cpp.cpp | cpp | safe | 0 | none | 1.326 | none |
| semgrep | safe_samples/502_java.java | java | safe | 0 | none | 36.688 (shared language batch) | none |
| semgrep | safe_samples/502_javascript.js | javascript | safe | 0 | none | 38.511 (shared language batch) | none |
| njsscan | safe_samples/502_javascript.js | javascript | safe | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | safe_samples/502_python.py | python | safe | 0 | none | 2.551 | none |
| ruff | safe_samples/502_python.py | python | safe | 0 | none | 0.542 | none |
| semgrep | safe_samples/502_python.py | python | safe | 0 | none | 49.267 (shared language batch) | none |
| semgrep | safe_samples/78_c.c | c | safe | 0 | none | 29.283 (shared language batch) | none |
| flawfinder | safe_samples/78_c.c | c | safe | 1 | CWE-78 | 1.048 | none |
| cppcheck | safe_samples/78_c.c | c | safe | 0 | none | 1.475 | none |
| semgrep | safe_samples/78_cpp.cpp | cpp | safe | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | safe_samples/78_cpp.cpp | cpp | safe | 1 | CWE-78 | 0.966 | none |
| cppcheck | safe_samples/78_cpp.cpp | cpp | safe | 0 | none | 1.444 | none |
| semgrep | safe_samples/78_java.java | java | safe | 0 | none | 36.688 (shared language batch) | none |
| semgrep | safe_samples/78_javascript.js | javascript | safe | 0 | none | 38.511 (shared language batch) | none |
| njsscan | safe_samples/78_javascript.js | javascript | safe | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | safe_samples/78_python.py | python | safe | 3 | CWE-78 | 2.447 | none |
| ruff | safe_samples/78_python.py | python | safe | 2 | CWE-78 | 0.233 | none |
| semgrep | safe_samples/78_python.py | python | safe | 0 | none | 49.267 (shared language batch) | none |
| semgrep | safe_samples/79_c.c | c | safe | 0 | none | 29.283 (shared language batch) | none |
| flawfinder | safe_samples/79_c.c | c | safe | 1 | CWE-134 | 1.239 | none |
| cppcheck | safe_samples/79_c.c | c | safe | 0 | none | 1.457 | none |
| semgrep | safe_samples/79_cpp.cpp | cpp | safe | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | safe_samples/79_cpp.cpp | cpp | safe | 0 | none | 1.134 | none |
| cppcheck | safe_samples/79_cpp.cpp | cpp | safe | 0 | none | 1.464 | none |
| semgrep | safe_samples/79_java.java | java | safe | 0 | none | 36.688 (shared language batch) | none |
| semgrep | safe_samples/79_javascript.js | javascript | safe | 0 | none | 38.511 (shared language batch) | none |
| njsscan | safe_samples/79_javascript.js | javascript | safe | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | safe_samples/79_python.py | python | safe | 0 | none | 2.632 | none |
| ruff | safe_samples/79_python.py | python | safe | 0 | none | 0.215 | none |
| semgrep | safe_samples/79_python.py | python | safe | 2 | CWE-79 | 49.267 (shared language batch) | none |
| semgrep | safe_samples/89_c.c | c | safe | 0 | none | 29.283 (shared language batch) | none |
| flawfinder | safe_samples/89_c.c | c | safe | 0 | none | 0.955 | none |
| cppcheck | safe_samples/89_c.c | c | safe | 0 | none | 1.471 | none |
| semgrep | safe_samples/89_cpp.cpp | cpp | safe | 0 | none | 29.974 (shared language batch) | none |
| flawfinder | safe_samples/89_cpp.cpp | cpp | safe | 0 | none | 1.108 | none |
| cppcheck | safe_samples/89_cpp.cpp | cpp | safe | 0 | none | 1.482 | none |
| semgrep | safe_samples/89_java.java | java | safe | 0 | none | 36.688 (shared language batch) | none |
| semgrep | safe_samples/89_javascript.js | javascript | safe | 0 | none | 38.511 (shared language batch) | none |
| njsscan | safe_samples/89_javascript.js | javascript | safe | UNSUPPORTED | none | 0.000 | Windows: libsast disables its Semgrep engine; no semantic scan ran |
| bandit | safe_samples/89_python.py | python | safe | 0 | none | 2.596 | none |
| ruff | safe_samples/89_python.py | python | safe | 0 | none | 0.180 | none |
| semgrep | safe_samples/89_python.py | python | safe | 0 | none | 49.267 (shared language batch) | none |

## Measurement notes

- Fixture files: 52 (26 vulnerable, 26 safe). Each is under 15 lines.
- Tool errors/timeouts are visible in the warning column and are not treated as no findings.
- The JavaScript CWE-78 and Java CWE-89 batch discrepancy was in the test/report lookup, not Semgrep: the batch result key already contained the suffix, but the test appended it again and substituted an empty list. After fixing the lookup, the current batch results include both detections; the Java raw CLI report also lists the CWE-89 finding in both single and batch scans.
- Post-change Semgrep batch wall times: Python 49.267s, JavaScript 38.511s, Java 36.688s, C 29.283s, C++ 29.974s. The outer Semgrep subprocess timeout is now 120 seconds; the per-rule timeout remains 10 seconds.
- njsscan 1.0.1 is installed and includes its rules, but `libsast` 3.1.8's `invoke_semgrep` returns `None` on Windows. The CLI therefore exits successfully with empty `nodejs` and `templates` objects; these are not clean scan results. The runner now reports njsscan as unsupported on Windows, and the API includes that limitation in `analysis_warnings`.
- Remaining language/CWE pairs with no exact mapped finding: c CWE-79, c CWE-89, cpp CWE-502, cpp CWE-79, cpp CWE-89, java CWE-78, javascript CWE-502.

## Real `/api/analyze` request timings

The following measurements were taken on 2026-10-01, before the custom Semgrep
configuration was added. One vulnerable fixture per language was submitted through
the running FastAPI application with the model loaded and real static-analysis
runners enabled. Request timing excludes application/model startup. All requests returned HTTP
200 and no analysis warnings.

| Language | Fixture | HTTP | Vulnerable | Findings | Seconds | Scan ID |
|---|---|---:|---:|---:|---:|---|
| python | `89_python.py` | 200 | true | 3 | 44.401 | `cd0a66a9-3548-4ffb-a095-6cd8334bc06e` |
| javascript | `78_javascript.js` | 200 | true | 2 | 33.746 | `f4792295-cbe3-4ca8-827a-87f42667b834` |
| java | `89_java.java` | 200 | true | 2 | 29.852 | `55eed065-a669-4a58-aa56-9fb43bb55821` |
| c | `120_c.c` | 200 | true | 5 | 24.406 | `a5bcdde2-39db-4700-aa7d-ed6b16be5a86` |
| cpp | `120_cpp.cpp` | 200 | true | 3 | 23.265 | `af6001db-b817-4058-a448-b1230653708a` |

## Generated 2,000-line input timings

The direct runners processed valid, generated source with 2,000 lines per
language. These timings came from the post-custom-rule test run. Semgrep's
elapsed value is for one fixture scan; it is not split into a per-file value.
The outer Semgrep subprocess limit was increased to 120 seconds. njsscan is
reported as unsupported on Windows, not as a successful zero-finding scan.

| Language | Tool | Findings | Seconds | Warning |
|---|---|---:|---:|---|
| python | Bandit | 0 | 3.590 | none |
| python | Ruff | 0 | 0.182 | none |
| python | Semgrep | 0 | 47.580 | none |
| javascript | Semgrep | 0 | 62.313 | none |
| javascript | njsscan | UNSUPPORTED | 0.000 | Windows: libsast disables its Semgrep engine |
| java | Semgrep | 0 | 43.700 | none |
| c | Semgrep | 0 | 36.841 | none |
| c | Flawfinder | 0 | 1.997 | none |
| c | Cppcheck | 0 | 3.608 | none |
| cpp | Semgrep | 0 | 40.133 | none |
| cpp | Flawfinder | 0 | 2.472 | none |
| cpp | Cppcheck | 0 | 4.413 | none |

## Final validation

- The first post-change `python -m pytest -v -s tests/test_tool_matrix.py` run exposed 14 Semgrep assertion failures caused by the suffix-doubling lookup documented above. After fixing the lookup, the focused Semgrep and Windows njsscan-warning tests passed: 41 passed, 14 xfailed, 75 deselected, 3 warnings in 743.96 seconds.
- The frontend was unchanged; its last recorded `npm run build` passed before these backend-only changes.
