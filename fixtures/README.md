# Controlled demonstration

The checkout fixture has a deliberately duplicated coupon application. It is synthetic and dependency-free. The first candidate only changes its own test to accept the incorrect result; the repaired candidate changes the implementation. Both are real commits generated locally by the fixture setup, not a claimed public customer incident.

The verifier's check is stored separately in runner/harness/check.py. Repository tests and the frozen behavioral contract are distinct evidence. Do not execute arbitrary submitted repositories through this demo endpoint.
