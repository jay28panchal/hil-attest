# Contributing

Issues and focused pull requests are welcome.

## Development

~~~console
python -m venv .venv
.venv/bin/python -m pip install -e .
python -m unittest discover -s tests -v
~~~

Keep the core compatible with Python 3.10 and free of required third-party
dependencies. New output fields must be deterministic and compatible with the
in-toto Statement and Test Result predicate.

Tests that need real hardware must be clearly marked and must identify the
board family without publishing raw serial numbers or other unique identifiers.

## Pull requests

- Explain the use case and threat-model impact.
- Add tests for behavior changes.
- Update documentation when the CLI or output changes.
- State whether testing used fixtures, emulation, or physical hardware.

