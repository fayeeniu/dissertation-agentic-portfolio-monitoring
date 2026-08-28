/**
 * Control-room enhancement.
 *
 * Two jobs, both derived only from state already rendered by the server:
 *   1. progressive disclosure — one stage inspector at a time;
 *   2. a user-initiated compressed replay of the persisted stage transitions.
 *
 * It never invents a stage, a status, a duration, or a handoff. A stage that the
 * server did not render as recorded is never replayed, and the static markup
 * remains complete when this module does not run.
 */

const rail = document.querySelector("[data-agent-rail]");
const inspectorColumn = document.querySelector(".inspector-column");
const stageNodes = [...document.querySelectorAll("[data-inspector-target]")];
const inspectors = [...document.querySelectorAll(".stage-inspector")];
const narrowLayout = window.matchMedia("(max-width: 1000px)");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

const RECORDED_STATES = ["complete", "failed", "needs-review", "approved", "exported", "rejected", "held", "working", "queued", "skipped"];
const STEP_GAP_MS = 320;
const HANDOFF_MS = 460;

let selectedInspector;

/* ---------------------------------------------------------------- inspector */

function restoreInspectorColumn() {
  if (!inspectorColumn) return;
  inspectors
    .slice()
    .sort((left, right) => Number(left.dataset.stageOrder) - Number(right.dataset.stageOrder))
    .forEach((inspector) => inspectorColumn.append(inspector));
}

function stepFor(inspector) {
  const key = inspector.id.replace("inspector-", "");
  return rail?.querySelector(`[data-stage="${CSS.escape(key)}"]`) ?? null;
}

function inspectorFromFragment() {
  const target = location.hash ? document.querySelector(location.hash) : null;
  return target?.classList.contains("stage-inspector") ? target : null;
}

function placeInspector(inspector) {
  if (!inspector) return;
  selectedInspector = inspector;
  inspectors.forEach((candidate) => {
    candidate.open = candidate === inspector;
  });
  rail?.querySelectorAll(".rail-step-selected").forEach((step) => step.classList.remove("rail-step-selected"));
  stepFor(inspector)?.classList.add("rail-step-selected");
  if (narrowLayout.matches) {
    stepFor(inspector)?.append(inspector);
  } else {
    restoreInspectorColumn();
  }
}

function activateInspector(event) {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const node = event.currentTarget;
  const inspector = document.getElementById(`inspector-${node.dataset.inspectorTarget}`);
  if (!inspector) return;

  event.preventDefault();
  placeInspector(inspector);
  inspector.querySelector("summary")?.focus({ preventScroll: true });
  inspector.scrollIntoView({ block: "nearest", behavior: reducedMotion.matches ? "auto" : "smooth" });
  history.replaceState(null, "", `#${inspector.id}`);
}

/* ------------------------------------------------------------------ replay */

function recordedSteps() {
  if (!rail) return [];
  return [...rail.querySelectorAll(".rail-step")].filter((step) =>
    RECORDED_STATES.some((state) => step.classList.contains(`rail-step-${state}`)),
  );
}

function createReplayControls(steps) {
  const host = document.querySelector("[data-circuit-controls]");
  if (!host || steps.length < 2) return null;

  const button = document.createElement("button");
  button.type = "button";
  button.className = "secondary";
  button.textContent = "Replay recorded trace";

  const state = host.querySelector(".replay-state");
  const live = document.createElement("p");
  live.className = "visually-hidden";
  live.setAttribute("role", "status");
  live.setAttribute("aria-live", "polite");

  host.prepend(button);
  host.append(live);
  return { button, state, live };
}

function clearReplay(steps) {
  rail?.removeAttribute("data-replay-running");
  steps.forEach((step) => {
    step.classList.remove("rail-step-replay-active", "rail-step-replay-done", "rail-step-sending");
  });
}

function setUpReplay() {
  const steps = recordedSteps();
  const controls = createReplayControls(steps);
  if (!controls) return;

  const { button, state, live } = controls;
  const idleCopy = state?.textContent ?? "";
  let token = 0;
  let running = false;

  const wait = (ms) =>
    new Promise((resolve) => {
      const delay = reducedMotion.matches ? Math.min(ms, 60) : ms;
      setTimeout(resolve, delay);
    });

  async function play() {
    const current = ++token;
    running = true;
    clearReplay(steps);
    rail?.setAttribute("data-replay-running", "true");
    button.textContent = "Stop replay";
    if (state) state.textContent = `Compressed replay · real durations stay in the inspector`;

    for (let index = 0; index < steps.length; index += 1) {
      if (current !== token) return;
      const step = steps[index];
      step.classList.add("rail-step-replay-active");
      const label = step.querySelector(".node-title")?.textContent?.trim() ?? "Stage";
      const status = step.querySelector(".node-state")?.textContent?.trim() ?? "";
      live.textContent = `Step ${index + 1} of ${steps.length}. ${label}: ${status}.`;
      await wait(STEP_GAP_MS);
      if (current !== token) return;
      step.classList.remove("rail-step-replay-active");
      step.classList.add("rail-step-replay-done");
      if (index + 1 < steps.length && step.classList.contains("rail-step-complete")) {
        step.classList.add("rail-step-sending");
        await wait(reducedMotion.matches ? 0 : HANDOFF_MS);
        step.classList.remove("rail-step-sending");
      }
    }

    if (current !== token) return;
    running = false;
    button.textContent = "Replay recorded trace";
    if (state) state.textContent = idleCopy;
    live.textContent = "Replay complete. The rail is showing the last persisted state.";
    clearReplay(steps);
  }

  function stop() {
    token += 1;
    running = false;
    clearReplay(steps);
    button.textContent = "Replay recorded trace";
    if (state) state.textContent = idleCopy;
    live.textContent = "Replay stopped. The rail is showing the last persisted state.";
  }

  button.addEventListener("click", () => (running ? stop() : play()));
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && running) stop();
  });
}

/* ------------------------------------------------------------------- start */

document.documentElement.classList.add("control-room-enhanced");
selectedInspector =
  inspectorFromFragment() ??
  inspectors.find((inspector) => inspector.dataset.initialOpen === "true") ??
  inspectors[0];
placeInspector(selectedInspector);
stageNodes.forEach((node) => node.addEventListener("click", activateInspector));
narrowLayout.addEventListener("change", () => placeInspector(selectedInspector));
window.addEventListener("hashchange", () => {
  const inspector = inspectorFromFragment();
  if (inspector) placeInspector(inspector);
});
setUpReplay();
