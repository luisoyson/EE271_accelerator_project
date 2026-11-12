# Trace schema, version 0

A trace records one simulator run so the viewer can replay it. It is the API
between the backend (simulator + recorder) and the frontend (viewer). The
validator is `viz/schema.py`; `make verify` checks every file in `traces/`.

## Top level

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | `0` | Bumped on any incompatible change. |
| `synthetic` | bool | `true` if hand-written rather than recorded from the simulator. |
| `description` | string | One line on what the run is. |
| `preset` | string | A name from `/api/presets`; fixes PE count and all widths. |
| `events` | list | In the order the calls happened. |

## Events

Each event is **one call** the accelerator made into a component, with that
component's state **right after** the call. Repeats (`Count + 1`) are separate
events. The schema does not assume an order between the memory call and the
PE calls in one step: it records whatever order the simulator used.

| Field | Type | Meaning |
|---|---|---|
| `seq` | int | Equal to the event's position in `events`. |
| `instr_index` | int ≥ 0 | Which program instruction; never decreases. |
| `repeat` | int ≥ 0 | Which of the `Count + 1` repetitions. |
| `component` | `"mem"` or `"pe"` | Main buffer or one PE. |
| `pe` | int | PE index; only on `pe` events. |
| `instr` | object | Decoded instruction (below). |
| `state` | object | State after the call (below). |

### `mem` events

`instr`: `opcode` (`READ`, `WRITE`, `NOP`), `mode` (8, 16, 32),
`mema_offset`, `memb_offset` (the offsets for this repeat, ≥ 0).

`state`:

- `mem0_port`: list of `pe_count` words, PE *i*'s slice of the MEM0 output.
- `mem1_port`: one word, the MEM1 output.
- `mem2_write`: `null`, or `{"addr": int, "words": [pe_count words]}` if this
  call wrote MEM2.

### `pe` events

`instr`: `opcode` (`MAC`, `NOP`, `OUT`, `PASS`, `CLR`, `RND`), `mode`,
`value` (0–31, used by `RND`).

`state`: `input_a`, `input_b`, `acc`, `out`, each one word.

## Words

```json
{"bits": 64, "lanes": [5, -3], "hex": "0xfffffffd00000005"}
```

- `bits`: the register width (input 32, accumulator 64, output 32 in all
  presets). Must match the config.
- `lanes`: signed values, **least-significant lane first**, split by the
  event's mode. Each must fit in `bits / lanes` signed bits.
- `hex`: the raw word, lowercase and zero-padded, or `null`.

v0 does not check that `hex` and `lanes` agree, because that check needs lane
packing, which is part of the graded work. The recorder (Thursday) adds it.
