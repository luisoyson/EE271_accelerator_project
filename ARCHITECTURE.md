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
| Viewer | Draws the hardware view (b) and the execution view (a) from a trace | Agent |

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

## Repo layout

TBD until the starter code is in the repo. The first agent proposes it.

## `docker/`

TBD. The first agent proposes the image, matching the course
`requirements.yml`.
