"""
Attention Scores — ManimCE Scene
=================================
Video implementation of the SAME outline as ./index.html: one query vector
Q, four key vectors K1..K4, a raw dot-product-style score per key, softmax
turning those into a weight distribution, the formula earned only after the
picture, and a closing "blended output" vector built from the weights.

Colors are the dark-theme hex values from index.html's CSS custom
properties (--q/--k/--w/--out), since Manim's default background is black —
same legend, same meaning, just the variant that reads on a dark canvas
instead of a light one.

No LaTeX/MathTex is used here — see this repo's README for why (this repo
renders with manim.Text() rather than requiring a full TeX install). If you
do have LaTeX available, swap the two Text() calls in beat_5_formula for
MathTex and you'll get typeset notation instead of the ASCII rendering below.

Render:
  uv run manim -pql examples/attention-scores/scene.py AttentionScores   # quick draft
  uv run manim -pqh examples/attention-scores/scene.py AttentionScores   # final quality
"""

import numpy as np
from manim import *

Q_COLOR = "#82A3F2"
K_COLOR = "#F0A468"
W_COLOR = "#F0C24D"
OUT_COLOR = "#C79BEA"
MUTED = "#8A94A5"

# Fixed geometry — never changes across beats. Only what's drawn ON TOP of
# these six directions changes (rule 2: one held metaphor).
Q_ANGLE = 90
K_ANGLES = [60, 130, 200, 20]
K_LABELS = ["K1", "K2", "K3", "K4"]

# Same illustrative raw scores as index.html, ordered consistently with how
# aligned each key's angle is with Q.
RAW_SCORES = [2.4, 1.7, -1.1, 0.3]
_EXP = [np.exp(v) for v in RAW_SCORES]
_EXP_SUM = sum(_EXP)
PROBS = [v / _EXP_SUM for v in _EXP]  # softmax(RAW_SCORES) ~= [0.61, 0.30, 0.02, 0.07]

ORIGIN_PT = np.array([-4.0, 0.3, 0])
VEC_LEN = 2.0

BAR_XS = [1.0, 2.0, 3.0, 4.0]
BAR_WIDTH = 0.6
RAW_BASELINE_Y = -0.3
RAW_SCALE = 0.55
SOFTMAX_BASELINE_Y = -2.2
SOFTMAX_SCALE = 3.0


def vector_end(angle_deg, length=VEC_LEN, origin=ORIGIN_PT):
    a = np.radians(angle_deg)
    return origin + length * np.array([np.cos(a), np.sin(a), 0])


def make_bar(x, value, baseline_y, color, scale):
    h = max(abs(value) * scale, 0.02)
    rect = Rectangle(
        width=BAR_WIDTH, height=h, color=color, fill_color=color,
        fill_opacity=0.9, stroke_width=0,
    )
    y = baseline_y + h / 2 if value >= 0 else baseline_y - h / 2
    rect.move_to(np.array([x, y, 0]))
    return rect


class AttentionScores(Scene):
    """How Q·Kᵀ scores become softmax attention weights, and what those
    weights mean: a blend of the keys, earned geometrically before the
    formula is shown."""

    def construct(self):
        self.show_legend()
        self.beat_1_query_and_one_key()
        self.beat_2_more_keys()
        self.beat_3_raw_scores()
        self.beat_4_softmax()
        self.beat_5_formula()
        self.beat_6_blended_output()
        self.wait(1)

    # ------------------------------------------------------------------
    # Legend — declared once, up front (rule 3: fixed color-to-meaning).
    # ------------------------------------------------------------------
    def show_legend(self):
        entries = [
            (Q_COLOR, "Q (query vector)"),
            (K_COLOR, "Ki (key vectors)"),
            (W_COLOR, "attention weight"),
            (OUT_COLOR, "blended output"),
        ]
        items = VGroup()
        for color, label in entries:
            swatch = Square(side_length=0.18, fill_color=color, fill_opacity=1, stroke_width=0)
            text = Text(label, font_size=20, color=MUTED)
            text.next_to(swatch, RIGHT, buff=0.15)
            items.add(VGroup(swatch, text))
        items.arrange(RIGHT, buff=0.55).to_edge(UP, buff=0.4)
        self.play(FadeIn(items))
        self.legend = items
        self.wait(0.3)

    # ------------------------------------------------------------------
    # Beat 1 — pure geometry, no formula (rule 1).
    # ------------------------------------------------------------------
    def beat_1_query_and_one_key(self):
        self.q_vec = Arrow(ORIGIN_PT, vector_end(Q_ANGLE), buff=0, color=Q_COLOR, stroke_width=6)
        self.q_label = Text("Q", font_size=26, color=Q_COLOR).next_to(self.q_vec.get_end(), UP, buff=0.1)

        self.k_vecs = [None, None, None, None]
        self.k_labels = [None, None, None, None]
        k0 = Arrow(ORIGIN_PT, vector_end(K_ANGLES[0]), buff=0, color=K_COLOR, stroke_width=6)
        k0_label = Text(K_LABELS[0], font_size=26, color=K_COLOR).next_to(k0.get_end(), UP, buff=0.1)
        self.k_vecs[0] = k0
        self.k_labels[0] = k0_label

        caption = Text(
            "A query and a key are each just a vector — a direction. Nothing has been compared yet.",
            font_size=24,
        ).to_edge(DOWN, buff=0.5)
        self.caption = caption

        self.play(FadeIn(self.q_vec), FadeIn(self.q_label), FadeIn(k0), FadeIn(k0_label), FadeIn(caption))
        self.wait(1.2)

    # ------------------------------------------------------------------
    # Beat 2 — add the rest of the keys. Same objects, more of them.
    # ------------------------------------------------------------------
    def beat_2_more_keys(self):
        new_caption = Text(
            "There isn't one key, there's one per token in context. Four keys, one query.",
            font_size=24,
        ).to_edge(DOWN, buff=0.5)

        anims = [Transform(self.caption, new_caption)]
        for i in range(1, 4):
            vec = Arrow(ORIGIN_PT, vector_end(K_ANGLES[i]), buff=0, color=K_COLOR, stroke_width=6)
            label = Text(K_LABELS[i], font_size=26, color=K_COLOR).next_to(vec.get_end(), UP, buff=0.1)
            self.k_vecs[i] = vec
            self.k_labels[i] = label
            anims += [FadeIn(vec), FadeIn(label)]

        self.play(*anims)
        self.wait(1.2)

    # ------------------------------------------------------------------
    # Beat 3 — raw dot-product-style scores, drawn as signed bars.
    # ------------------------------------------------------------------
    def beat_3_raw_scores(self):
        new_caption = Text(
            "The raw score is a dot product: how aligned each key is with the query. "
            "Aligned = high score. Opposite = negative.",
            font_size=22,
        ).to_edge(DOWN, buff=0.5)

        self.bars = []
        self.bar_labels = []
        anims = [Transform(self.caption, new_caption)]
        for i in range(4):
            bar = make_bar(BAR_XS[i], RAW_SCORES[i], RAW_BASELINE_Y, W_COLOR, RAW_SCALE)
            name = Text(K_LABELS[i], font_size=18, color=MUTED).next_to(
                np.array([BAR_XS[i], RAW_BASELINE_Y - 1.0, 0]), DOWN, buff=0.05
            )
            value_label = Text(f"{RAW_SCORES[i]:+.1f}", font_size=18, color=WHITE)
            value_label.next_to(bar, UP if RAW_SCORES[i] >= 0 else DOWN, buff=0.08)
            self.bars.append(bar)
            self.bar_labels.append(value_label)
            anims += [FadeIn(bar), FadeIn(name), FadeIn(value_label)]

        baseline = Line(
            np.array([BAR_XS[0] - 0.7, RAW_BASELINE_Y, 0]),
            np.array([BAR_XS[-1] + 0.7, RAW_BASELINE_Y, 0]),
            color=MUTED, stroke_width=1,
        )
        anims.append(FadeIn(baseline))
        self.baseline = baseline

        self.play(*anims)
        self.wait(1.2)

    # ------------------------------------------------------------------
    # Beat 4 — softmax: same bars, morphed into a positive distribution
    # that sums to one. The transform IS the explanation (rule 4).
    # ------------------------------------------------------------------
    def beat_4_softmax(self):
        new_caption = Text(
            "Softmax turns raw scores into a probability distribution: all positive, "
            "summing to one. The best-aligned key now dominates.",
            font_size=22,
        ).to_edge(DOWN, buff=0.5)

        new_bars = []
        new_labels = []
        for i in range(4):
            bar = make_bar(BAR_XS[i], PROBS[i], SOFTMAX_BASELINE_Y, W_COLOR, SOFTMAX_SCALE)
            label = Text(f"{round(PROBS[i] * 100)}%", font_size=18, color=WHITE).next_to(bar, UP, buff=0.08)
            new_bars.append(bar)
            new_labels.append(label)

        new_baseline = Line(
            np.array([BAR_XS[0] - 0.7, SOFTMAX_BASELINE_Y, 0]),
            np.array([BAR_XS[-1] + 0.7, SOFTMAX_BASELINE_Y, 0]),
            color=MUTED, stroke_width=1,
        )
        sum_ref = DashedLine(
            np.array([BAR_XS[0] - 0.7, 1.0, 0]),
            np.array([BAR_XS[-1] + 0.7, 1.0, 0]),
            color=MUTED, stroke_width=1,
        )
        sum_label = Text("sum of weights = 1", font_size=16, color=MUTED).next_to(sum_ref, UP, buff=0.08)

        anims = [Transform(self.caption, new_caption), Transform(self.baseline, new_baseline),
                 FadeIn(sum_ref), FadeIn(sum_label)]
        for old_bar, new_bar in zip(self.bars, new_bars):
            anims.append(Transform(old_bar, new_bar))
        for old_label, new_label in zip(self.bar_labels, new_labels):
            anims.append(ReplacementTransform(old_label, new_label))
        self.bar_labels = new_labels
        self.sum_ref = VGroup(sum_ref, sum_label)

        self.play(*anims)
        self.wait(1.2)

    # ------------------------------------------------------------------
    # Beat 5 — the formula, earned only now. Vectors/bars dim to bring it
    # forward, never removed (rule 2 — still the same held picture).
    # ------------------------------------------------------------------
    def beat_5_formula(self):
        new_caption = Text(
            "Made precise, that's the whole rule.", font_size=24,
        ).to_edge(DOWN, buff=0.5)

        formula_1 = Text("score(Q, Ki) = (Q . Ki) / sqrt(d)", font_size=30, color=WHITE)
        formula_2 = Text("weight_i = softmax(score)_i", font_size=26, color=MUTED)
        formula = VGroup(formula_1, formula_2).arrange(DOWN, buff=0.25).move_to(np.array([0, 1.8, 0]))

        dim_group = VGroup(
            self.q_vec, self.q_label, *self.k_vecs, *self.k_labels,
            *self.bars, *self.bar_labels, self.baseline, self.sum_ref,
        )

        self.play(
            Transform(self.caption, new_caption),
            dim_group.animate.set_opacity(0.55),
            FadeIn(formula),
        )
        self.formula = formula
        self.wait(1.5)

    # ------------------------------------------------------------------
    # Beat 6 — bonus: the weights blend the SAME keys into one output
    # vector. No new diagram, only a derived arrow on the existing
    # picture (rule 2).
    # ------------------------------------------------------------------
    def beat_6_blended_output(self):
        new_caption = Text(
            "Those weights blend the keys' information into one output — "
            "mostly K1's direction, a little of K2's, almost none of K3's.",
            font_size=22,
        ).to_edge(DOWN, buff=0.5)

        sx = sum(p * np.cos(np.radians(a)) for p, a in zip(PROBS, K_ANGLES))
        sy = sum(p * np.sin(np.radians(a)) for p, a in zip(PROBS, K_ANGLES))
        blend_angle = np.degrees(np.arctan2(sy, sx))

        out_vec = Arrow(
            ORIGIN_PT, vector_end(blend_angle, length=VEC_LEN * 0.8),
            buff=0, color=OUT_COLOR, stroke_width=6,
        )
        out_label = Text("output", font_size=24, color=OUT_COLOR).next_to(out_vec.get_end(), RIGHT, buff=0.1)

        dim_group = VGroup(
            self.q_vec, self.q_label, *self.k_vecs, *self.k_labels,
            *self.bars, *self.bar_labels, self.baseline, self.sum_ref,
        )

        self.play(
            Transform(self.caption, new_caption),
            FadeOut(self.formula),
            dim_group.animate.set_opacity(0.85),
            FadeIn(out_vec), FadeIn(out_label),
        )
        self.wait(1.5)
