# Architecture

How this project is built. PROMPT.md says why and in what order; AGENTS.md
sets the rules. Keep this file true when the design changes.

## Components

| Component | Job | Written by |
|---|---|---|
| Simulator | The graded Python model of the SIMD accelerator (`processing_element.py`, `main_buffer.py`, `accelerator.py` in the course starter code) | Me |
| Reference model | Numpy matrix-level oracle (`C = A @ B`) for differential tests | Agent |
| Recorder | Runs the simulator and captures per-cycle state into a trace | Agent |
| Trace schema | Versioned JSON format for one run; the API between backend and frontend | Agent |
| Server | Serves traces and the viewer locally | Agent |
| Viewer | Draws the hardware view (b), the PE instruction view, and the execution view (a) from a trace | Agent |
| ISA reference | What each PE instruction does, at the spec's abstraction level, with field widths from the course config. No encodings (decoding is graded work) | Agent |

## Data flow

```
instructions + data ──► Simulator ◄── Recorder ──► trace.json ──► Server ──► Viewer
                            │
                            └──► outputs ──► differential test ◄── Reference model
```

## Mapping to the AGENTS.md invariants

- **Backend** = simulator + recorder. Every value shown is one the simulator
  produced.
- **API** = the trace schema, served by the server.
- **Frontend** = the viewer. It draws and handles interaction only. It never
  recomputes, corrects or derives a simulator value for display.
- The server binds to `127.0.0.1` only.
- All dependencies are installed when the image is built.

## Design decisions

- **The trace is the contract.** A recorder captures per-cycle state from the
  simulator into a versioned JSON trace. The viewer only draws traces. The
  trace schema is the API: document it, validate it, and test it.
- **Graded files stay clean.** Record from outside the simulator (wrapping or
  inspecting objects from a runner) so the graded files contain no
  visualization code. If the starter API makes that impossible, propose the
  smallest hook and wait for approval.
- **Serving:** use the smallest local server that satisfies the AGENTS.md
  invariants. Prefer standard-library or already-justified dependencies. No
  frontend frameworks unless justified in the plan.

- **Recorder hooks (Thursday):** wrap `execute_instruction` on the main
  buffer instance and on each PE instance at run time, and read the
  accelerator's private `_main_buffer` / `_pe_array`. Acceptable for a
  debugging tool, and it needs no change to the graded files.
- **Configs** come from the course's own
  `generate_accelerator_and_instruction_configuration` (`viz/configs.py`),
  so the drawing matches what the tests instantiate. Lane geometry is
  computed there, not in the viewer.
- **No lane packing in `viz/` before the graded helpers exist.** Packing and
  unpacking lanes is graded work; the v0 schema therefore does not check
  `hex` against `lanes`. See docs/trace_schema.md.

## Repo layout

```
simd-part1/          course starter (code.stanford.edu, .git removed)
  src/               graded: processing_element.py, main_buffer.py, accelerator.py
  test/              course tests; test/src symlinks to ../src
viz/
  configs.py         presets + lane geometry
  isa.py             PE instruction reference (effects only, no encodings)
  schema.py          trace schema v0 validator; `python -m viz.schema <dir>`
  server.py          stdlib HTTP server and API routes
  static/            index.html, app.js, style.css (plain SVG/JS, no framework)
traces/              trace JSON files served by the API
tests/               pytest suite for viz/
docs/                assignment PDF, trace_schema.md
docker/Dockerfile
Makefile             every command; `make help`
```

`PYTHONPATH` is `/work:/work/simd-part1`, so `viz` imports the starter as
`src.*`, the same way the course tests do.

## `docker/`

One image, `ee271-simd`, from `python:3.13.5-slim` (the course's Python),
with `make` so the course test Makefile runs unchanged. Packages are pinned in
`requirements.txt` and installed at build. The repo is bind-mounted at `/work`
and the container runs as an unprivileged user. `make serve` publishes the
server on `127.0.0.1` only; inside the container it binds `0.0.0.0` because
Docker's port forwarding needs that.
