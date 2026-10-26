# Prompt: discover a new open-source project idea

Copy everything below into a deep-research-capable AI. This prompt starts with
no preferred project and requires the researcher to find, challenge, rank, and
select an idea from current evidence.

---

Act as a senior open-source strategist, embedded-systems architect, developer
tools product researcher, and skeptical technical investor.

I want to create and maintain a genuinely useful public open-source project.
First perform deep research to discover the best project idea for my skills.
Do not begin with a predetermined solution. Do not optimize for a grant, free
subscription, GitHub stars, or an impressive-looking repository. Optimize for a
real recurring problem, clear users, technical differentiation, maintainability,
and a credible path to authentic adoption.

## My technical background

Use this background to determine founder/project fit:

- Embedded C and C++ firmware
- Python and shell automation
- Nordic nRF52 and nRF54 devices
- Zephyr and nRF Connect SDK
- Bluetooth Low Energy and device commissioning
- UART, USB serial, SEGGER J-Link, RTT, GDB, and firmware debugging
- Raspberry Pi CM4 and OpenWrt gateways
- Linux system integration
- AWS IoT and edge/cloud communication
- Cross-platform desktop tooling with Qt
- Firmware flashing, factory workflows, field diagnostics, and release support

I can test with embedded hardware, but I am initially a solo maintainer. Prefer
an MVP that one experienced developer can build in four to eight weeks and
maintain incrementally. The project may be a CLI, library, GitHub Action,
protocol/specification with reference implementation, desktop utility, or a
focused service. Do not assume a GUI is necessary.

## Legal and ethical constraints

- The project must be original or legitimately built on compatible
  open-source components.
- Do not copy source code, confidential workflows, credentials, product
  details, or intellectual property from employers or private repositories.
- Do not propose fake accounts, fabricated adoption, artificial stars,
  misleading benchmarks, or grant manipulation.
- Clearly separate open standards from vendor-specific licenses and SDK terms.
- Identify trademark, patent, export-control, device-security, or licensing
  concerns when relevant.
- The repository must have a real open-source license before publication.

## Research objective

Find an underserved problem at the intersection of embedded development,
firmware maintenance, device testing, Linux/edge systems, and open-source
maintainer workflows. The winning project should provide a capability that
existing tools do not provide well, or make a fragmented workflow materially
simpler, safer, or more interoperable.

## Research areas

Investigate all of these areas before selecting candidates:

1. Hardware-in-the-loop testing and evidence
2. Firmware crash analysis and postmortem debugging
3. UART, RTT, SWO, GDB, and OpenOCD workflows
4. Zephyr and nRF Connect SDK developer pain points
5. BLE interoperability, commissioning, and field diagnostics
6. OpenWrt and Raspberry Pi edge-gateway maintenance
7. Firmware release provenance, signing, SBOMs, and update safety
8. Factory flashing, provisioning, and reproducibility
9. Offline-first diagnostic tools for field engineers
10. Multi-device test labs and USB-device coordination
11. Embedded CI for projects without permanent cloud hardware
12. Migration tools between SDK, board, or operating-system versions
13. Agent-assisted firmware development with truthful hardware verification
14. Maintainer automation for triage, releases, compatibility, and security

Also investigate adjacent areas suggested by the evidence. Do not force the
answer into this list.

## Evidence collection

Browse current sources rather than relying on memory.

For each research area:

- Read official documentation and current release notes.
- Search canonical GitHub/GitLab issue trackers and discussions for recurring
  unresolved pain.
- Examine existing repositories, their activity, open issues, governance,
  license, adoption, and roadmap.
- Look for repeated manual scripts or documentation procedures that could
  become a reusable tool.
- Identify recently deprecated tools, abandoned projects, incompatible
  operating-system support, and fragmented vendor workflows.
- Find maintainers explicitly requesting help, integrations, or replacement
  tooling.
- Distinguish user complaints from proven willingness to install and maintain
  another tool.
- Prefer primary sources. Use forums or Reddit only as supplementary demand
  evidence, never as the sole technical source.

Every material claim must have a direct citation. Label inference and
uncertainty.

## Ideas to reject early

Reject or heavily penalize:

- another generic serial terminal;
- a generic log viewer with no unique workflow;
- another AI chat wrapper;
- a generic dashboard, TODO app, expense manager, or CRUD application;
- a thin wrapper around one command with no interoperability or safety value;
- a project whose only differentiator is “uses AI”;
- a clone of a mature tool with thousands of users and active maintenance;
- a project requiring proprietary hardware or paid cloud services for basic use;
- a project too broad for one maintainer to produce a credible MVP;
- an idea whose usefulness depends on unverified or misleading claims;
- a repository that would initially contain only documentation and placeholder
  code unless a specification itself is the validated need.

## Candidate generation

Generate at least twelve candidate projects. Each candidate must include:

- name and one-sentence description;
- target user;
- exact painful workflow;
- primary evidence that the problem exists;
- current workaround;
- closest competitors;
- specific differentiation;
- why my background is a fit;
- four-to-eight-week MVP;
- required hardware and external services;
- cross-platform scope;
- security and privacy concerns;
- likely maintenance burden;
- path to the first five genuine users;
- reasons the idea might fail.

Ideas should be meaningfully different, not variations of the same product.

## Competitive analysis

For every serious candidate, compare at least five relevant substitutes. Build
a table containing:

- project and canonical URL;
- license;
- latest meaningful activity;
- stars/downloads only as contextual signals;
- active maintainers and governance;
- supported platforms and hardware;
- core features;
- important missing feature;
- open issues demonstrating the gap;
- whether contributing upstream is better than a new repository.

If a mature maintained project can accept the proposed capability cleanly,
recommend an upstream contribution rather than unnecessary fragmentation.

## Scoring model

Score every candidate from 1 to 5 using this weighted model:

- Proven problem evidence: 20%
- Unserved or poorly served gap: 15%
- Fit with my skills and available hardware: 15%
- MVP feasibility in four to eight weeks: 10%
- Potential ecosystem importance: 10%
- Path to authentic external users: 10%
- Long-term maintainability for one person: 10%
- Security and trust value: 5%
- Cross-platform or broad applicability: 5%

Show raw scores, weighted score, evidence quality, and confidence. Do not
silently adjust weights to make a preferred idea win.

Apply a penalty for:

- crowded market;
- dependence on proprietary APIs;
- uncertain licensing;
- high support burden;
- expensive hardware matrix;
- weak proof that users care;
- an MVP that cannot demonstrate its core claim.

## Falsification

For the top six candidates, actively search for evidence that invalidates the
idea. Ask:

- Does a current tool already solve this?
- Is the problem rare rather than recurring?
- Is the workaround already easy?
- Would users trust or install this tool?
- Is the hardest part organizational rather than technical?
- Does the idea require integrations I cannot realistically maintain?
- Would an upstream patch have greater impact?
- Can usefulness be demonstrated without fabricated adoption?

Reject at least six of the twelve candidates and explain why.

## Top-three validation

For the three strongest candidates, provide:

1. A precise problem statement
2. Primary user persona
3. Current workflow diagram
4. Proposed workflow diagram
5. Competitor matrix
6. Technical architecture
7. Threat model
8. MVP specification
9. Explicit non-goals
10. Test and hardware-validation strategy
11. License recommendation
12. Initial repository structure
13. First ten GitHub issues
14. Documentation and demo plan
15. Thirty-, sixty-, and ninety-day validation plan
16. Stop conditions

Include five non-leading interview questions for prospective users and identify
which answers would disprove the idea.

## Selection

Select exactly one recommendation:

- CREATE A NEW REPOSITORY
- CONTRIBUTE UPSTREAM
- BUILD A SMALL EXPERIMENT BEFORE DECIDING
- NO-GO, CONTINUE SEARCHING

The selection must follow the evidence and scoring. A no-go conclusion is valid
and preferable to manufacturing a weak repository.

If recommending a new repository, provide:

- final project name after GitHub, PyPI/npm/crates, domain, and trademark checks;
- memorable tagline;
- user and problem;
- clear differentiation;
- recommended MIT or Apache-2.0 license with tradeoff explanation;
- programming language and dependency strategy;
- package layout;
- CLI/API contract;
- sample input and output;
- data model or protocol;
- security model;
- CI matrix;
- unit, integration, simulation, and real-hardware test plan;
- release and signing plan;
- contribution and governance files;
- MVP milestone with acceptance criteria;
- first public demo;
- outreach list of relevant communities and maintainers;
- truthful README wording that does not overclaim maturity.

## Adoption validation

Define measurable goals that demonstrate real value rather than vanity:

### First 30 days

- number of maintainer interviews;
- design feedback from relevant upstream communities;
- working MVP acceptance tests;
- one reproducible public example;
- one real-hardware result clearly labeled.

### First 60 days

- external trial users;
- issues created by people other than the author;
- integrations or example projects;
- first tagged release;
- compatibility and limitation documentation.

### First 90 days

- returning external users;
- external contributors or reviewers;
- production or release workflow pilots;
- upstream collaboration;
- evidence supporting continue, pivot, or stop.

Do not use a star target as the primary success metric.

## Open-source support program assessment

Only after selecting the technically strongest idea, read the current official
Codex for Open Source criteria and program terms.

Explain:

- why no project can guarantee selection;
- what objective evidence the program may consider;
- why a brand-new repository is not equivalent to an active, important project;
- what could truthfully be claimed at launch;
- what maintenance and adoption evidence would be needed before applying;
- whether applying immediately would be premature.

Never recommend creating a repository solely to obtain a program benefit.

## Required final report

Return the research in this exact order:

1. Executive summary
2. Method and source-quality rules
3. Twenty recurring problems discovered
4. Twelve candidate project ideas
5. Candidate scoring matrix
6. Six or more rejected ideas and reasons
7. Top-three detailed evaluations
8. Final selection and rationale
9. Full repository specification for the winner
10. Four-to-eight-week implementation plan
11. Thirty-/sixty-/ninety-day validation plan
12. Risks, falsification criteria, and stop conditions
13. Honest open-source program-fit assessment
14. Prioritized next actions
15. Direct links to all primary sources

End with one unambiguous sentence:

“My recommendation is to ______ because ______.”

---

