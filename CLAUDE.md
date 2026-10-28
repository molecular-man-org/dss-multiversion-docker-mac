# dss-mac-docker — notes for Claude sessions

Read this first; it holds the facts that are easy to get wrong.

## Licences

Full reference: [docs/LICENCES.md](docs/LICENCES.md). The essentials:

- **Licence files live in `~/.dataiku/licenses/`.** This is the repo standard,
  the default of `DSS_LAB_LICENSE_DIR`, and what new users are told to use. Never
  copy a licence file into the repo, and never commit one.
- **Match the licence type to the DSS version and package era.** Canonical
  maximum-productive-access profile per type:

  ```text
  2025 -> FULL_DESIGNER    (requires DSS 12.6.0 or later)
  2024 -> DESIGNER         (FY2021-FY2024 packages; the default)
  2018 -> DATA_SCIENTIST   (legacy profiles; old instances only)
  ```

- **The three "2025" licences must not be used on DSS older than 12.6.0.** Older
  DSS rejects them, and `dsscli set-license` can still exit 0.
- **"Maximum access" means the top productive designer profile, never an
  administrative one.** Do not use `PLATFORM_ADMIN`, `ADMIN` or
  `TECHNICAL_ACCOUNT` to get more features; admin rights are assigned separately.

## Working rules

- Local Docker DSS nodes may be changed freely; internet-hosted DSS nodes never.
- Run at most two DSS nodes at once (the Docker VM's memory is the limit).
- `bash tests/run_tests.sh` needs no Docker; `markdownlint .` and `shellcheck` run
  in the same gate.
- Run `scripts/check.sh` before committing: tests, shellcheck and markdownlint in
  one command, with a real exit code. CI should run the same command.

## Writing docs

- Wrap prose at 80 columns as you write. Tables and code fences are exempt (see
  `.markdownlint.yaml`). Run `markdownlint <file>` right after each doc write,
  before the next command.

## Shell and test gotchas

- Scripts must run on macOS (bash 3.2, BSD userland) and on Linux (GNU, the CI
  matrix). Avoid flags that exist on only one: `declare -A`, `sort -V`,
  `pgrep -c`, `cat -A`, `tail -r`. `sed -i` needs `-i ''` on macOS.
- In `tests/run_tests.sh`, call any sourced function that can `die` inside a
  subshell `( … )`. `sh -c` loses sourced functions.
- Wait for long jobs with a background `until <check>; do sleep 2; done`, never
  a bare `sleep N`.

## Probing a DSS API

- Use `dss-lab api <spec> <METHOD> <path> [json]` for calls to a local node. It
  refuses non-local nodes, keeps the key out of `ps`, and always ends with an
  `HTTP <code>` line, so a status is never mistaken for an empty result.
- Take field names and enum values from the SDK source
  (`dataiku-api-client-python`) or the server's error text. After two guessed
  variants, stop and write down what is known and unknown.
- Every probe table carries a control that must return the opposite answer: a
  path known to exist, a parent object known to exist. 400 means the route
  exists. 403 can mean the parent project is missing. 404 on both eras is
  probably a wrong path. None of these alone is evidence of absence.
