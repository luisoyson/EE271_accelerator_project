// Hardware view (b): draws Figure 3 of the spec from /api/config.
// The backend supplies every number (widths, depths, lane geometry); this
// file only lays out and labels.
"use strict";

const SVG_NS = "http://www.w3.org/2000/svg";

const state = {
  config: null,       // from /api/config
  mode: "16",         // key into config.modes
  selected: null,     // {kind, index?}
};

// What each block does, paraphrased from the spec (sections 3.1-3.3).
const BLOCK_INFO = {
  mem0: (c) => ({
    title: "MEM0: matrix memory",
    text: [
      `Each address holds one row ${c.memories.mem0.bitwidth} bits wide: one ` +
      `${c.pe.input_bitwidth}-bit word per PE.`,
      "READ uses MemAOffset as the address. Each PE gets its own word as input B: " +
      "this is the \"multiple data\" in SIMD.",
    ],
  }),
  mem1: (c) => ({
    title: "MEM1: vector memory",
    text: [
      `Each address holds one ${c.memories.mem1.bitwidth}-bit word.`,
      "READ uses MemBOffset. In INT16/INT8 the lowest offset bit(s) choose a sub-word, " +
      "which is repeated to fill the whole word.",
      "The same word goes to every PE as input A (the broadcast).",
    ],
  }),
  mem2: (c) => ({
    title: "MEM2: output memory",
    text: [
      `Each address holds ${c.memories.mem2.bitwidth} bits: one ` +
      `${c.pe.output_bitwidth}-bit output per PE.`,
      "WRITE stores every PE's output register at MemAOffset.",
    ],
  }),
  ctl: () => ({
    title: "Controller",
    text: [
      "Fetches one instruction: MemInstruction | PEInstruction | Count MemAInc MemBInc.",
      "Sends the memory instruction to the main buffer and the same PE instruction to every PE " +
      "(the \"single instruction\" in SIMD).",
      "Repeats it Count + 1 times, adding MemAIncrement and MemBIncrement to the offsets each time.",
    ],
  }),
  imem: () => ({
    title: "Instruction memory",
    text: ["Holds the program the compiler produced (see src/compiler.py)."],
  }),
};

// ------------------------------------------------------------ data access

async function getJSON(url) {
  const resp = await fetch(url);
  const body = await resp.json();
  if (!resp.ok) throw new Error(body.error || `${resp.status} from ${url}`);
  return body;
}

function showError(err) {
  const box = document.getElementById("error");
  box.textContent = `Error: ${err.message}`;
  box.hidden = false;
  console.error(err);
}

// ------------------------------------------------------------ SVG helpers

function el(name, attrs = {}, parent = null) {
  const node = document.createElementNS(SVG_NS, name);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (parent) parent.appendChild(node);
  return node;
}

function block(svg, { x, y, w, h, cls, label, sub, select }) {
  const g = el("g", { class: `block ${cls}`, tabindex: "0", role: "button", "aria-label": label }, svg);
  el("rect", { x, y, width: w, height: h }, g);
  el("text", { x: x + w / 2, y: y + h / 2 - (sub ? 7 : 0) }, g).textContent = label;
  if (sub) el("text", { x: x + w / 2, y: y + h / 2 + 9, class: "sub" }, g).textContent = sub;
  const choose = () => { state.selected = select; render(); };
  g.addEventListener("click", choose);
  g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); choose(); } });
  const sel = state.selected;
  if (sel && sel.kind === select.kind && sel.index === select.index) g.classList.add("selected");
  return g;
}

function wire(svg, points, cls = "") {
  el("polyline", { points: points.map((p) => p.join(",")).join(" "), class: `wire ${cls}` }, svg);
}

function arrowHead(svg, x, y, dir = "right") {
  const s = 5;
  const pts = {
    right: [[x, y], [x - s * 1.6, y - s], [x - s * 1.6, y + s]],
    down: [[x, y], [x - s, y - s * 1.6], [x + s, y - s * 1.6]],
  }[dir];
  el("polygon", { points: pts.map((p) => p.join(",")).join(" "), class: "arrow" }, svg);
}

function label(svg, x, y, text, anchor = "start") {
  el("text", { x, y, class: "wire-label", "text-anchor": anchor }, svg).textContent = text;
}

// ------------------------------------------------------------ drawing

function drawHardware() {
  const c = state.config;
  const svg = document.getElementById("hw");
  svg.replaceChildren();

  const n = c.pe_count;
  const pitch = n > 16 ? 30 : 48;
  const peH = pitch - 12;
  const top = 120;
  const colH = Math.max(n * pitch - 12, 140);
  const W = 780;

  const mem0 = { x: 40, y: top, w: 150, h: colH };
  const pe = { x: 360, w: 110 };
  const mem2 = { x: 600, y: top, w: 150, h: colH };
  const mem1 = { x: pe.x - 5, y: 20, w: 120, h: 54 };
  const busX = 320;
  const peY = (i) => top + i * pitch;

  // MEM1 broadcast bus: down from MEM1, then a tap into every PE.
  const lastTap = peY(n - 1) + peH * 0.7;
  wire(svg, [[mem1.x + mem1.w / 2, mem1.y + mem1.h], [mem1.x + mem1.w / 2, 96], [busX, 96], [busX, lastTap]], "a");
  label(svg, busX - 6, 90, "input A: broadcast to all PEs", "end");

  for (let i = 0; i < n; i++) {
    const y = peY(i);
    // MEM0 → PE (input B, one word per PE)
    wire(svg, [[mem0.x + mem0.w, y + peH * 0.3], [pe.x, y + peH * 0.3]], "b");
    arrowHead(svg, pe.x, y + peH * 0.3);
    // MEM1 bus tap → PE (input A)
    wire(svg, [[busX, y + peH * 0.7], [pe.x, y + peH * 0.7]], "a");
    el("circle", { cx: busX, cy: y + peH * 0.7, r: 3, class: "dot" }, svg);
    arrowHead(svg, pe.x, y + peH * 0.7);
    // PE → MEM2 (output)
    wire(svg, [[pe.x + pe.w, y + peH / 2], [mem2.x, y + peH / 2]]);
    arrowHead(svg, mem2.x, y + peH / 2);
    block(svg, {
      x: pe.x, y, w: pe.w, h: peH, cls: "pe",
      label: `PE ${i}`, select: { kind: "pe", index: i },
    });
  }
  label(svg, mem0.x + mem0.w + 8, top - 8, "input B: one word per PE");
  label(svg, pe.x + pe.w + 8, top - 8, "output → MEM2");

  const m = c.memories;
  block(svg, { ...mem0, cls: "mem", label: "MEM0", sub: `${m.mem0.bitwidth}b × ${m.mem0.depth}`, select: { kind: "mem0" } });
  block(svg, { ...mem1, cls: "mem", label: "MEM1", sub: `${m.mem1.bitwidth}b × ${m.mem1.depth}`, select: { kind: "mem1" } });
  block(svg, { ...mem2, cls: "mem", label: "MEM2", sub: `${m.mem2.bitwidth}b × ${m.mem2.depth}`, select: { kind: "mem2" } });

  // Controller and instruction memory below the array.
  const bottom = top + colH;
  const ctl = { x: 300, y: bottom + 60, w: 130, h: 46 };
  const imem = { x: 470, y: bottom + 60, w: 130, h: 46 };
  wire(svg, [[ctl.x, ctl.y + ctl.h / 2], [mem0.x + mem0.w / 2, ctl.y + ctl.h / 2], [mem0.x + mem0.w / 2, bottom]], "ctl");
  wire(svg, [[ctl.x + ctl.w / 2, ctl.y + ctl.h], [ctl.x + ctl.w / 2, ctl.y + ctl.h + 16],
             [mem2.x + mem2.w / 2, ctl.y + ctl.h + 16], [mem2.x + mem2.w / 2, bottom]], "ctl");
  wire(svg, [[ctl.x + ctl.w / 2, ctl.y], [ctl.x + ctl.w / 2, bottom + 24], [pe.x + pe.w / 2, bottom + 24],
             [pe.x + pe.w / 2, peY(n - 1) + peH]], "ctl");
  label(svg, pe.x + pe.w / 2 + 6, bottom + 20, "same PE instruction to every PE");
  label(svg, mem0.x + mem0.w / 2 + 6, ctl.y + ctl.h / 2 - 6, "memory instruction");
  wire(svg, [[imem.x, imem.y + imem.h / 2], [ctl.x + ctl.w, ctl.y + ctl.h / 2]]);
  arrowHead(svg, ctl.x + ctl.w, ctl.y + ctl.h / 2);
  block(svg, { ...ctl, cls: "ctl", label: "Controller", sub: `counter ${c.counter_bitwidth}b`, select: { kind: "ctl" } });
  block(svg, { ...imem, cls: "ctl", label: "Inst. Mem", select: { kind: "imem" } });

  const H = ctl.y + ctl.h + 40;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("width", W);
  svg.setAttribute("height", H);
}

// ------------------------------------------------------------ side panel

function html(tag, text, cls) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (cls) node.className = cls;
  return node;
}

function defList(pairs) {
  const dl = html("dl");
  for (const [k, v] of pairs) { dl.append(html("dt", k), html("dd", String(v))); }
  return dl;
}

// One register drawn as lanes; lane 0 (least significant) sits on the right.
function register(title, bits, laneBits, source) {
  const wrap = html("div", undefined, "reg");
  const head = html("div", undefined, "reg-title");
  head.append(html("strong", `${title} · ${bits} bits`), html("span", source, "muted"));
  const lanes = html("div", undefined, "lanes");
  lanes.style.width = `${(bits / state.config.pe.accumulation_bitwidth) * 100}%`;
  const count = bits / laneBits;
  for (let i = 0; i < count; i++) {
    const lane = html("div", undefined, "lane");
    lane.append(
      html("div", `lane ${i}`),
      html("div", "—", "val"),
      html("div", `[${(i + 1) * laneBits - 1}:${i * laneBits}]`, "bits"),
    );
    lanes.append(lane);
  }
  wrap.append(head, lanes);
  return wrap;
}

function renderSummary() {
  const c = state.config;
  const g = c.modes[state.mode];
  const box = document.getElementById("summary");
  box.replaceChildren(
    html("h2", c.description),
    defList([
      ["PEs", c.pe_count],
      ["PE input / acc / output", `${c.pe.input_bitwidth} / ${c.pe.accumulation_bitwidth} / ${c.pe.output_bitwidth} bits`],
      [`Lanes in INT${state.mode}`, `${g.lanes} per word`],
      ["Lane widths (in / acc / out)", `${g.input_lane_bits} / ${g.acc_lane_bits} / ${g.output_lane_bits} bits`],
    ]),
  );
}

function renderDetail() {
  const c = state.config;
  const g = c.modes[state.mode];
  const box = document.getElementById("detail");
  const sel = state.selected;
  if (!sel) {
    box.replaceChildren(html("p", "Select a block in the diagram.", "muted"));
    return;
  }
  if (sel.kind !== "pe") {
    const info = BLOCK_INFO[sel.kind](c);
    box.replaceChildren(html("h3", info.title), ...info.text.map((t) => html("p", t)));
    return;
  }
  box.replaceChildren(
    html("h3", `PE ${sel.index} in INT${state.mode}`),
    html("p", `Same instruction as every other PE, different data. Each of the ${g.lanes} lane(s) ` +
      "is computed independently; values are signed two's complement."),
    register("Input A", c.pe.input_bitwidth, g.input_lane_bits, "from MEM1 (broadcast)"),
    register("Input B", c.pe.input_bitwidth, g.input_lane_bits, "from MEM0 (this PE's word)"),
    register("Accumulator", c.pe.accumulation_bitwidth, g.acc_lane_bits, "internal"),
    register("Output", c.pe.output_bitwidth, g.output_lane_bits, "to MEM2"),
    html("p", "Values appear here once a trace from your simulator is loaded (execution view).", "muted"),
  );
}

function render() {
  drawHardware();
  renderSummary();
  renderDetail();
}

// ------------------------------------------------------------ wiring

async function loadPreset(name) {
  state.config = await getJSON(`/api/config?preset=${encodeURIComponent(name)}`);
  state.mode = String(state.config.default_mode);
  state.selected = null;
  document.getElementById("mode").value = state.mode;
  render();
}

async function init() {
  const { default: def, presets } = await getJSON("/api/presets");
  const select = document.getElementById("preset");
  for (const p of presets) {
    const opt = document.createElement("option");
    opt.value = p.name;
    opt.textContent = p.description;
    select.append(opt);
  }
  select.value = def;
  select.addEventListener("change", () => loadPreset(select.value).catch(showError));
  document.getElementById("mode").addEventListener("change", (e) => { state.mode = e.target.value; render(); });
  await loadPreset(def);
}

init().catch(showError);
