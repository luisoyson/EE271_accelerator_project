# EE271 SIMD Accelerator, Part 1

A Python simulator of the EE271 SIMD matrix-multiply accelerator (the course
assignment, in `simd-part1/`), plus a browser visualizer for learning how it
works. Why and how the project is run: [PROMPT.md](PROMPT.md). How it is
built: [ARCHITECTURE.md](ARCHITECTURE.md).

## Requirements

Docker and `make`. Nothing else is installed on the host.

## Quick start

```sh
make build         # build the image (once, or after requirements.txt changes)
make serve         # visualizer at http://127.0.0.1:8000 (Ctrl-C to stop)
```

## Targets

| Target | What it does |
|---|---|
| `make help` | List targets. |
| `make build` | Build the Docker image. |
| `make starter-test` | Run the course's public tests (`simd-part1/test`), all of them even if some fail. |
| `make test` | Run this repo's tests (visualizer, schema, server). |
| `make verify` | The gate: `make test` plus validating every trace in `traces/`. |
| `make serve` | Run the visualizer on `127.0.0.1:8000` (`PORT=9000 make serve` to change). |
| `make shell` | Shell inside the container. |
| `make freeze` | Print installed package versions, for pinning. |

`make verify` does not include `starter-test`: the course tests fail until the
graded files are implemented.

## Grading

The local container mirrors the course environment (Python 3.13.5 and the same
packages), but grading uses caddy with the course conda environment. Before
submitting, run on caddy, inside `simd-part1/`:

```sh
cd test && make run_tests
cd .. && make generate_submission
```

## Layout

```
simd-part1/   course starter code; only the three graded files are edited
viz/          visualizer: config presets, trace schema, server, static viewer
traces/       recorded runs (sample.json is a synthetic fixture)
tests/        tests for viz/
docs/         assignment PDF and the trace schema
docker/       Dockerfile
```
