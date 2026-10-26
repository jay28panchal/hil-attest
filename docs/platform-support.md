# Platform support

hil-attest is dependency-free Python and does not access serial ports or debug
probes itself. The test harness produces JUnit and evidence files; hil-attest
reads those files and writes JSON.

## Minimum supported systems

| Platform | Minimum | Processor | Notes |
|---|---|---|---|
| Ubuntu | 24.04 LTS | x86-64 | Earlier Linux releases may work with Python 3.10+, but are not the support baseline. |
| Windows | Windows 11 25H2 | x86-64 | Use a currently serviced Home, Pro, Enterprise, or Education edition. |
| macOS | macOS 15 Sequoia | Apple silicon or Intel | Apple silicon is exercised by the `macos-15` hosted runner. |

All platforms require CPython 3.10 or newer. A practical minimum is 512 MB of
available memory and 100 MB of free disk space in addition to Python and the
input files. JUnit XML is parsed in memory, while firmware and evidence files
are hashed in streaming chunks. Very large JUnit reports therefore require
additional memory proportional to the XML document.

These are maintained support baselines, not claims that older systems cannot
run the program. Windows 10 servicing ended in October 2025. Ubuntu 24.04 LTS
has standard security maintenance through 2029. Apple's security release list
still covers macOS 15 in 2026. The baseline should be reviewed at least once per
year rather than silently promising support for an unpatched host OS.

## Continuous integration

Every push and pull request runs the same install, 18-test suite, and example
round trip on:

- Ubuntu 24.04, Python 3.10 and 3.13;
- Windows Server 2025, Python 3.10 and 3.13;
- macOS 15, Python 3.10 and 3.13.

Windows Server 2025 exercises the Windows Python/filesystem code path in GitHub
Actions; the user-facing minimum remains Windows 11 25H2. CI does not verify
USB drivers, debug probes, or a physical HIL bench because hil-attest does not
control those devices.

## Source references

- Microsoft Windows lifecycle:
  https://learn.microsoft.com/windows/release-health/windows11-release-information
- Apple security releases: https://support.apple.com/100100
- Ubuntu release cycle: https://ubuntu.com/about/release-cycle
- GitHub-hosted runner images: https://github.com/actions/runner-images
