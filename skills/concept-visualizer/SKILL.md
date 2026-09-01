---
name: concept-visualizer
description: Use when explaining a math, ML, or LLM-architecture concept visually and interactively in 3Blue1Brown's style — "visualize X", "animate how X works", "show me X geometrically" — or when the same concept also needs a rendered video walkthrough. Produces a learner-driven HTML explainer and/or a ManimCE video, built from one shared step outline.
---

# Concept Visualizer

Explains ONE concept the way 3Blue1Brown does: geometric intuition first, one
held visual metaphor, a fixed color-to-meaning mapping, and continuous
morphing between states — never a wall of prose, never a jump-cut slide deck.

This skill produces output in **two formats that share one design contract**:

1. **HTML explainer** — a single self-contained page, `<canvas>`-driven, that
   the learner clicks through at their own pace (Prev/Next, arrow keys, a
   dot-per-step progress strip). No autoplay.
2. **Manim video** — a real [ManimCE](https://www.manim.community/) `Scene`
   rendered to `.mp4`, for when a video artifact is genuinely what's wanted
   (embedding, sharing outside a browser, a passive watch instead of an
   interactive one).

These are **not interchangeable renderings of the same code** — they are two
separate implementations of one shared outline. Pick one, the other, or both,
depending on what the learner/consumer needs. Building both roughly doubles
authoring effort; that's a deliberate tradeoff for genuinely native output in
each format (a screen-recorded canvas makes a mediocre video; a browser
wrapped around an embedded video makes a mediocre interactive page).

## The four authoring rules (non-negotiable gates)

These apply identically to both output formats — they are properties of the
*explanation*, not of the medium:

1. **Geometric intuition before formula.** Step 1 / beat 1 is always a
   picture or spatial arrangement, never an equation. The formula (if any)
   appears only after the picture has made the "why" obvious — usually 3–4
   beats in.
2. **One held metaphor.** Pick a single visual object (a vector, a grid, a
   rotating point, a stack of blocks) and transform it across every
   step/beat. Never introduce a second unrelated diagram mid-explanation —
   that's a sign the concept should be split into two visualizations.
3. **Fixed color-to-meaning mapping.** Declare a legend once, before step 1 /
   beat 1. A color never means two different things across steps. Use the
   *same* hex values in both the HTML and the Manim `Scene` for a given
   concept, so the two artifacts read as the same explanation.
4. **Continuity, not jump-cuts.** State changes between steps/beats animate
   (morph/rotate/grow/fade), never instant swaps. In HTML this is a ~500ms
   `requestAnimationFrame` lerp; in Manim it's `Transform`/`ReplacementTransform`/
   `.animate` — never `Scene.add()` a whole new Mobject where a transform of
   the existing one would do. The transformation itself must carry meaning —
   if a beat doesn't visibly change from the last, it's not a real beat.

## The shared step/beat outline — the source of truth

Authoring a concept means writing **one** step/beat outline first, then
implementing it **twice**. The outline, not either implementation, is the
source of truth — if the HTML and the video ever disagree on what a step
shows, the outline is what's right and one of the implementations has
drifted.

Write the outline as a numbered list, one entry per step/beat:

```
Step N — <one-line name>
  Caption:  <the one sentence a learner reads/hears at this step>
  Visual:   <what's on screen — described purely geometrically>
  Change from previous step: <what moves/morphs/appears — must be non-trivial>
  Legend touched: <which held object(s) this step concerns — must be a subset
                   of the legend declared at step 0>
```

5–9 entries. Step/beat 1 must have no formula in "Visual". Draft this before
touching `template.html` or `template_manim.py` — getting the outline right
is the part most likely to go wrong, and it's far cheaper to fix in a bullet
list than in canvas math or Manim positioning code.

## Workflow

1. Identify the ONE concept (not a cluster — "attention" often splits into
   "Q·K scoring" and "softmax weighting" as two visualizations; pick one).
2. Draft the step/beat outline above, checked against the four rules.
3. Decide which output(s) you're building: HTML, Manim video, or both.
4. **HTML:** copy `template.html`, fill in the `AUTHOR:` blocks per the
   outline. Keep the file self-contained — no external fonts/scripts, inline
   everything. Open locally (`open <file>.html`) to check it, and/or publish
   via the Artifact tool (follow `artifact-design` for
   typography/palette/theming if publishing that way).
5. **Manim:** copy `template_manim.py`, fill in the `AUTHOR:` blocks — one
   method per beat, called in sequence from `construct()`. Render locally
   (see "Rendering the Manim side" below) and watch the output before calling
   it done; Manim's default camera framing and text sizing surprise people.
6. If building both, do a final side-by-side pass: same colors, same object
   count, same number of real state changes. They should feel like the same
   explanation in two media, not two different explanations that happen to
   share a topic.

## Shape of the HTML output

One HTML file, `<canvas>` for the visual, a small step state machine:
Prev/Next buttons, arrow-key support, a dot-per-step progress strip. 5–9
steps, matching the outline 1:1. Each step pairs one caption sentence with
one visual state. No autoplay, no localStorage — state is just the current
step index in memory; the file itself is static.

Copy `template.html` in this directory for the CSS/state-machine scaffold
(`AUTHOR:` comments mark what to fill in).

## Shape of the Manim output

One `Scene` subclass in a `.py` file, one method per beat (`beat_1_...`,
`beat_2_...`, etc.), called in order from `construct()`. Beats are discrete —
each ends with a `self.wait()` and a clear before/after state — not one
continuous ad-hoc animation improvised beat-to-beat. Reuse the same Mobjects
across beats via `Transform`/`.animate` rather than creating fresh ones, so
rule 4 (continuity) holds in video the same way it holds in the HTML lerp.

Copy `template_manim.py` in this directory for the scaffold (`AUTHOR:`
comments mark what to fill in, structured to mirror `template.html`'s step
list so the parallel is obvious).

### Setting up ManimCE

From this repo's root (uses this project's own environment — do not mix into
an unrelated Python project):

```bash
uv sync                    # installs manim + deps from pyproject.toml
brew install ffmpeg        # if not already present
```

Manim needs LaTeX only for `MathTex`/`Tex` (rendered mathematical notation).
If you don't have a LaTeX distribution, use `Text()` for any on-screen
notation instead — see the README for exactly what this repo does and why.
Installing a full TeX distribution (e.g. `brew install --cask
mactex-no-gui`) is a multi-GB, slow install; only do it if you actually need
typeset math rather than plain text equations.

### Rendering the Manim side

```bash
uv run manim -pql examples/attention-scores/scene.py AttentionScores   # quick draft (480p15)
uv run manim -pqh examples/attention-scores/scene.py AttentionScores   # final (1080p60)
```

`-p` previews (opens the video) after rendering, `-q{l,m,h,k}` sets quality.
Output lands in `./media/videos/<scene-file>/<quality>/<SceneName>.mp4` —
this `media/` cache is gitignored; copy the final approved render to a
committed path (see each example's own instructions) if it should ship with
the repo.

## Common mistakes

| Mistake | Correction |
|---|---|
| Formula shown in step/beat 1 "for context" | Formula is earned, not given upfront — cut it from early steps |
| Two diagrams for one concept | Split into two visualizations, or find the single metaphor that unifies them |
| A color reused for a different quantity later | Re-derive the legend; one color, one meaning, for the whole artifact |
| Steps that just add text without changing the visual | Not a real step — merge it into the adjacent one or add real visual motion |
| Autoplay / timeline-driven HTML | This skill is learner-driven; add Prev/Next, not a play button |
| Manim beat that `self.add()`s a whole new Mobject instead of transforming | Breaks rule 4 in the video the same way an instant HTML swap would — use `Transform`/`.animate` |
| HTML and Manim versions disagree on colors, object count, or step order | They implement one outline — re-sync both against the outline, not against each other |
| Building both formats when only one was asked for | Confirm scope first; authoring both is ~2x the work for a reason |
