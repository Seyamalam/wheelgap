# LangChain Core: one test-dependency gap, fixed one release up

[LangChain](https://github.com/langchain-ai/langchain) is a framework for building applications with language models.
This study checks `langchain-core`, the package in the monorepo's `libs/core` directory. It pins revision
[`30c4e38d71c2fdf6af474e0bb21832491aaa983e`](https://github.com/langchain-ai/langchain/tree/30c4e38d71c2fdf6af474e0bb21832491aaa983e)
(langchain-core 1.8.5, committed on 26 November 2026), uses **wheelgap 0.14.0**, and records package availability
checked on **27 November 2026**.

## Input, selection and targets

The input is the unchanged [`libs/core/uv.lock`](https://github.com/langchain-ai/langchain/blob/30c4e38d71c2fdf6af474e0bb21832491aaa983e/libs/core/uv.lock),
with its adjacent [`pyproject.toml`](https://github.com/langchain-ai/langchain/blob/30c4e38d71c2fdf6af474e0bb21832491aaa983e/libs/core/pyproject.toml).

The package declares `requires-python = ">=3.11.0,<4.0.0"` and classifiers for Python 3.11 through 3.14. The
monorepo's [CI matrix script](https://github.com/langchain-ai/langchain/blob/30c4e38d71c2fdf6af474e0bb21832491aaa983e/.github/scripts/check_diff.py)
runs `libs/core` tests on Python 3.11, 3.12, 3.13 and 3.14. Its [test workflow](https://github.com/langchain-ai/langchain/blob/30c4e38d71c2fdf6af474e0bb21832491aaa983e/.github/workflows/_test.yml)
runs those jobs on `ubuntu-latest` and installs them with `uv sync --group test --dev`.

Accordingly, this scan checks:

- **Python:** 3.11, 3.12, 3.13 and 3.14
- **Platform:** `linux-x86_64`, reflecting the x86_64 Ubuntu CI runner
- **Dependency selection:** the project dependencies, uv's default `dev` group and the `test` group. wheelgap's
  `--group test` selection includes the project dependencies and default groups, so it matches the workflow's
  `uv sync --group test --dev` here.

The Linux target uses wheelgap's default glibc compatibility floor of 2.36; this is a scan assumption, not a measured
version from the CI runner.

## Reproduce

Download the two input files from the pinned revision:

```bash
B=https://raw.githubusercontent.com/langchain-ai/langchain/30c4e38d71c2fdf6af474e0bb21832491aaa983e
curl -fL $B/libs/core/uv.lock -o uv.lock
curl -fL $B/libs/core/pyproject.toml -o pyproject.toml
```

Run the scan with wheelgap 0.14.0:

```bash
uvx --python 3.12 --from wheelgap==0.14.0 wheelgap uv.lock \
  -p 3.11 -p 3.12 -p 3.13 -p 3.14 -t linux-x86_64 \
  --group test --explain --suggest --no-cache
```

The scan exited **1** and examined **146 index packages**. **145** had wheels for every target. Its table and the
gap's explanation were:

```text
package                           version  3.11 linux-x86_64  3.12 linux-x86_64  3.13 linux-x86_64  3.14 linux-x86_64
forbiddenfruit (via blockbuster)  0.1.4    ● source           ● source           ● source           ● source

145 packages with wheels for every target hidden (--all to show)

forbiddenfruit 0.1.4 on 3.11 linux-x86_64: ● source
  via: (test group) → blockbuster → forbiddenfruit
  no wheels published for this version

forbiddenfruit 0.1.4 -> 0.1.5 has wheels for 3.11 linux-x86_64, 3.12 linux-x86_64, 3.13 linux-x86_64, 3.14 linux-x86_64

skipped 2 non-index packages: langchain-core (editable), langchain-tests (directory)
1 of 146 packages has gaps: 1 will build from source.
```

(The explanation repeats once per Python; the three other rows are the same except for the target label.)

## The forbiddenfruit gap

`blockbuster` is in the `test` group, and it depends on `forbiddenfruit`. The locked forbiddenfruit 0.1.4, uploaded in
2021, publishes only an sdist, so every selected Python installs it with a source build.

`--suggest` names the fix one release up: **0.1.5** publishes a `py3-none-any` wheel. PyPI records that wheel as
uploaded on 25 November 2026, two days before this scan. This is a wheel-availability suggestion, not proof that the
update is compatible with LangChain; any update should go through the project's dependency constraints and tests.

pip agrees for the Python 3.14 `linux-x86_64` cell. This check asks pip for a binary-only install using every
manylinux x86_64 tag wheelgap's default glibc 2.36 floor accepts:

```bash
platforms="$(for m in $(seq 36 -1 5); do printf -- '--platform manylinux_2_%s_x86_64 ' "$m"; done)"
platforms="$platforms--platform manylinux2014_x86_64 --platform manylinux2010_x86_64 --platform manylinux1_x86_64"
python3 -m pip download --no-deps --only-binary=:all: --index-url https://pypi.org/simple -d /tmp/wg-check \
  $platforms --python-version 3.14 --implementation cp --abi cp314 forbiddenfruit==0.1.4
```

It fails with `No matching distribution found for forbiddenfruit==0.1.4` (and pip's version list contains only
0.1.5). The same command with `forbiddenfruit==0.1.5` downloads `forbiddenfruit-0.1.5-py3-none-any.whl`.

## Scope and limitations

This study reports wheel availability for the CI dependency selection on Linux. It does not establish that the
forbiddenfruit source build succeeds, nor does it test LangChain's runtime behavior. The two local non-index packages
are outside the index-package scan: `langchain-core` is the project itself, and `langchain-tests` is a directory
dependency used by the tests. Results may change when the lockfile or package files are updated.
