# PROMPT: EE271 SIMD Accelerator, Part 1

Repository standards live in AGENTS.md and are not repeated here. This file
says what the project is for and how to work on it.

## Goal

The point is **leverage**, not efficiency. Passing Part 1 is the floor, not the
target. In three days (deadline **Fri Nov 13, 11:59 PM PST**) I want to:

1. Learn how a SIMD accelerator works by building its Python simulator myself.
2. Not get stuck on tedious tangential work (environment, tooling, plumbing).
3. Actually absorb the material, not just get green tests.
4. Build skills that carry beyond this homework: reference models,
   differential testing, property-based testing.
5. Get better at Python: bit manipulation, `dataclasses`, type hints,
   `hypothesis`, observer-style hooks.

Spec: `docs/Project_Part_1.pdf`. Read all of it before your first plan.

## Who does what

The rule: **I write what is meant to be learned; you write what is tangential.**

| I write (you tutor) | You write |
|---|---|
| `processing_element.py`, `main_buffer.py`, `accelerator.py` logic | Container, Makefile targets, environment matching the course `requirements.yml` |
| Lane pack/unpack helpers and their unit tests | Numpy reference model (matrix level only, e.g. `C = A @ B`) |
| The properties each test asserts | `hypothesis` harness and differential-test plumbing around my properties |
| | Trace recorder, trace schema, server, both visualizations |

### Tutor mode (graded files)

For the three graded files, and for any code that is a direct piece of them,
you do **not** write solution code, even if I ask in a tired moment. Instead,
escalate one step at a time and only when I'm still stuck:

1. Ask me a question that points at the gap.
2. Point me to the exact sentence of the spec.
3. Give a small worked example with concrete numbers (not code).
4. Explain the Python idiom on an unrelated example.

You may review my code, name the spec rule I broke, and give an input that
breaks it. Treat EE271's AI policy as forbidding AI-written graded code until
I tell you otherwise.

## The spec details that matter

The private staff tests decide the grade, and these details are where a guessed
reading of the spec fails. Make sure I can explain each one, and that each has
a test:

- Lanes are signed two's complement. INT8 = 4 lanes, INT16 = 2, INT32 = 1,
  with the least-significant lane first. Accumulator lanes are wider (16/32/64
  bits). Python ints never overflow, so all masking and sign extension is
  explicit.
- **MAC** adds the full signed product into the wide lane and does not saturate.
- **OUT** clamps each lane to `[-2^(w-1), 2^(w-1)-1]`, then narrows and
  concatenates. The accumulator is left alone.
- **PASS** sign-extends each Data0 lane (the MEM1 broadcast) into its
  accumulator lane.
- **RND** divides by `2^s` with round-half-to-even, where `s` is the unsigned
  5-bit Value field. Do it in integer math, never with float `round()`.
- **CLR** zeroes the accumulator and the output register. Only OUT and CLR
  update the output register.
- **MEM1 READ** in INT16/INT8 uses the low offset bits (`[0]` or `[1:0]`) to
  pick a sub-word and the remaining bits as the address, then repeats the
  sub-word across the full word.
- **Controller**: each instruction runs `Count + 1` times. MemAOffset and
  MemBOffset increase by their increments on each repeat.
- The design is driven by its config object. Nothing is hard-coded.

## Visualizations: learning tools, not deliverables

Gradescope never sees these. They exist so I can see the architecture and
check that my logic does what I think it does. Two views share one page:

**(b) Hardware view, the stage.** An interactive drawing of Figure 3: MEM0,
MEM1, MEM2, the PE column, the controller and instruction memory, and the
wires. It is sized from the config (number of PEs, widths). Clicking a PE
opens it to show its accumulator split into lanes for the current mode. This
view is useful on day 1, before any of my code runs.

**(a) Execution view, the action.** I step forward and backward through
cycles, and the values my simulator actually produced appear on the stage:
the instruction being decoded, the MEM0/MEM1 reads, the broadcast to every
PE, accumulator updates per lane, OUT clamping, and the MEM2 write. Show
values in decimal with hex on demand. If my logic is wrong, the picture must
show the wrong value. Never "fix" or recompute anything for display.

How it's built: see ARCHITECTURE.md.

**Scope:** the hardware view comes before the execution view. Polish comes
last. If the visualization starts to threaten the deadline, stop and tell me.

## Starter code and privacy

- I bring in the starter code (`simd-part1` from code.stanford.edu). Don't
  fetch it. Propose where it lives in the repo and how the visualization code
  sits beside it without changing the structure of the graded files.
- Course solutions must not be public (Honor Code). Before your first push,
  ask me to confirm the GitHub repo is private.
- Grading runs on caddy with the course conda environment. Local container
  results do not count as passing. I run `make run_tests` and
  `make generate_submission` there myself.

## Milestones

| When | Me | You |
|---|---|---|
| Wed Nov 11 | Read the spec; lane helpers + PE, test-first | Container and Makefile; hardware view (b); trace schema draft |
| Thu Nov 12 | Main buffer + controller; properties for each tricky detail | Recorder; execution view (a); reference-model differential test across all modes |
| Fri Nov 13, by 3 PM | Pass on caddy, generate the submission | Help debug failures in tutor mode |
| Fri evening | Write `notes/LEARNINGS.md` | Polish the visualization only if everything above is done |

**Submittable on caddy by Friday afternoon** is the one milestone that can't
move. Everything else gives way to it.

## Done, for learning

- All public tests pass on caddy and the submission zip exists.
- Every item in "The spec details that matter" has at least one test, and I
  can explain each without notes.
- The differential test against the reference model passes for INT8, INT16
  and INT32 with randomized inputs.
- I can step through a full matrix-multiply trace in the viewer and narrate
  what the hardware is doing at each cycle.
- `notes/LEARNINGS.md` lists what I'd carry into Part 2 (RTL), especially
  which tests and the reference model I can reuse.

## Open decisions (ask me, don't assume)

- Changing EE271's AI-policy assumption in tutor mode.
- Any hook inside a graded file.
- Any dependency beyond Python, numpy, hypothesis and the course's own
  requirements.
