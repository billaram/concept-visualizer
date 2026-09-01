"""
Latent Reasoning — Mechanism — ManimCE Scene
=============================================
A deeper, paper-grounded companion to ./index.html. index.html tells the
accessible version of this story with an allegory (a legible chain of
stepping stones vs. a smooth continuous curve). This scene tells the SAME
underlying story — legible discrete reasoning vs. opaque continuous
reasoning — but grounded in the actual architecture of two real papers,
mechanism first, allegory second:

  SoftCoT     — Xu et al., arXiv:2502.12134 (ACL 2025)
  SoftCoT++   — Xu et al., arXiv:2505.11484

This is NOT a re-skin of index.html's outline. It holds one visual metaphor
(a point in embedding space, either snapped to the vocabulary grid or free)
and carries a single soft-thought Mobject through the entire pipeline: born
as a free point off the grid, produced by a frozen assistant model, projected
by the one trainable layer, spliced into a frozen backbone, then split and
pushed apart by a contrastive loss for test-time scaling. Every number cited
on screen (68.21% -> 70.52%, 81.96% -> 82.64%, 88.65% -> 90.05%, etc.) is
taken directly from the papers — see the brief this was built from for the
verification trail. Nothing here is derived or estimated.

No LaTeX/MathTex is used — Text() only (via the SafeText() wrapper below),
per this repo's convention (see README: no TeX distribution is installed or
assumed).

Render:
  uv run manim -pql examples/latent-reasoning/scene_mechanism.py LatentReasoningMechanism   # quick draft
  uv run manim -pqm examples/latent-reasoning/scene_mechanism.py LatentReasoningMechanism   # committed quality
"""

import numpy as np
from manim import *

# Manim's bundled default font renders as a dated serif on this machine.
# Arial reads cleanest for this technical content and is a standalone .ttf
# (not a .ttc collection), the commonly recommended safe default for Manim
# Text() on macOS.
Text.set_default(font="Arial")

# The actual bug (found the hard way, across many rendered frames, not
# guessed): Text() at font_size <= ~18 mis-shapes on this Pango build —
# broken mid-word kerning ("SoftC oT", "fro zen m odel") — REGARDLESS of
# font family (Arial/Verdana/Helvetica Neue all did it), ligatures, disk
# caching, or render resolution. Confirmed clean at font_size >= 20 for
# every broken string tested. A uniform .scale() AFTER Text() creation is
# safe (proven); creating directly at a small font_size, or scaling a
# VGroup that contains one, is not. Fix: every Text() call in this file
# goes through SafeText() below, which creates at a safe size and scales
# down to the size actually requested.
def SafeText(text, font_size=24, **kwargs):
    safe_size = max(font_size, 20)
    t = Text(text, font_size=safe_size, **kwargs)
    if safe_size != font_size:
        t.scale(font_size / safe_size)
    return t

# ----------------------------------------------------------------------
# Legend colors. SCRATCH/LATENT/GATE are the dark-theme hex values from
# index.html's CSS custom properties (--scratch/--latent/--gate) so this
# video and the HTML page read as the same explanation (rule 3). TRAIN is
# the one new color this piece introduces: "trainable, gradients flow
# here" — used ONLY for the projection layer, nowhere else. FROZEN boxes
# stay neutral grey with a dashed outline, never a semantic color.
# ----------------------------------------------------------------------
SCRATCH = "#E0A64C"   # amber — discrete, on-grid, legible (vocabulary tokens)
LATENT = "#9B90F0"    # violet — continuous, off-grid, opaque (soft thoughts)
GATE = "#5FC7A4"       # teal — training signal / contrastive loss
TRAIN = "#F2705A"      # warm coral — trainable projection layer (NEW)
MUTED = "#8A94A5"
FROZEN_FILL = "#1E2430"
INK = "#E6E9F0"

ARXIV_SOFTCOT = "arXiv:2502.12134 (ACL 2025)"
ARXIV_SOFTCOTPP = "arXiv:2505.11484"


# ------------------------------------------------------------------
# Small reusable builders
# ------------------------------------------------------------------
def frozen_box(center, w, h, title, sub="frozen — no gradients"):
    fill = Rectangle(width=w, height=h, color=MUTED, fill_color=FROZEN_FILL,
                      fill_opacity=1.0, stroke_width=0).move_to(center)
    outline = DashedVMobject(
        Rectangle(width=w, height=h, color=MUTED, stroke_width=3),
        num_dashes=int(2 * (w + h) * 2.2),
    ).move_to(center)
    title_txt = SafeText(title, font_size=22, color=INK, weight=BOLD).move_to(center + UP * (h / 2 - 0.42))
    sub_txt = SafeText(sub, font_size=14, color=MUTED).move_to(center + UP * (h / 2 - 0.75))
    # Explicit z-index: fill strictly behind outline/text, regardless of
    # VGroup submobject order, so text never gets occluded once fill_opacity
    # changes (e.g. dimming/restoring across beats).
    fill.set_z_index(0)
    outline.set_z_index(1)
    title_txt.set_z_index(2)
    sub_txt.set_z_index(2)
    return VGroup(fill, outline, title_txt, sub_txt)


def chip(text, color, font_size=15, w=0.95, h=0.42):
    box = RoundedRectangle(corner_radius=0.07, width=w, height=h, color=color,
                            fill_color=color, fill_opacity=0.16, stroke_width=2)
    txt = SafeText(text, font_size=font_size, color=color)
    if txt.width > w - 0.1:
        txt.scale_to_fit_width(w - 0.1)
    txt.move_to(box.get_center())
    box.set_z_index(0)
    txt.set_z_index(1)
    return VGroup(box, txt)


def pct_bar(x, value, baseline_y, color, scale, max_val=100):
    h = max(value * scale / max_val, 0.03)
    rect = Rectangle(width=0.9, height=h, color=color, fill_color=color,
                      fill_opacity=0.9, stroke_width=0)
    rect.move_to(np.array([x, baseline_y + h / 2, 0]))
    return rect


class LatentReasoningMechanism(Scene):
    """SoftCoT / SoftCoT++: how a soft-thought vector is produced, projected,
    spliced into a frozen backbone, trained through one linear layer, and
    (in SoftCoT++) pushed apart into M diverse candidates for test-time
    self-consistency. Mechanism-first companion to index.html's allegory."""

    def construct(self):
        self.show_legend()
        self.beat_1_vocab_grid()
        self.beat_2_free_point()
        self.beat_3_two_frozen_models()
        self.beat_4_assistant_produces_raw_thought()
        self.beat_5_projection_layer()
        self.beat_6_splice_and_decode()
        self.beat_7_gradient_flow()
        self.beat_8_first_numbers()
        self.beat_9_determinism_gap()
        self.beat_10_m_distinct_tokens()
        self.beat_11_contrastive_repulsion()
        self.beat_12_aggregation_and_numbers()
        self.beat_13_limitations()
        self.beat_14_close_on_tsoft()
        self.wait(1)

    # ------------------------------------------------------------------
    # Legend — declared once, up front (rule 3).
    # ------------------------------------------------------------------
    def show_legend(self):
        entries = [
            (SCRATCH, "vocabulary (discrete)"),
            (LATENT, "soft thought (continuous)"),
            (TRAIN, "trainable projection"),
            (GATE, "training signal"),
            (MUTED, "frozen model (dashed)"),
        ]
        # Rebuild at a smaller font_size rather than rescaling an already-built
        # VGroup, purely to keep the legend fitting within the frame — the
        # actual glyph-corruption fix (small font_size mis-shaping) lives in
        # SafeText() itself, used below via `text = SafeText(...)`.
        def build_items(font_size):
            grp = VGroup()
            for color, label in entries:
                swatch = Square(side_length=0.15, fill_color=color, fill_opacity=1, stroke_width=0)
                text = SafeText(label, font_size=font_size, color=MUTED)
                text.next_to(swatch, RIGHT, buff=0.1)
                grp.add(VGroup(swatch, text))
            grp.arrange(RIGHT, buff=0.38)
            return grp

        font_size = 16
        items = build_items(font_size)
        # Force-fit within the frame regardless of font metrics — the
        # legend must never clip off either edge.
        while items.width > 12.6 and font_size > 10:
            font_size -= 1
            items = build_items(font_size)
        items.to_edge(UP, buff=0.25)
        credit = SafeText(f"SoftCoT {ARXIV_SOFTCOT}  ·  SoftCoT++ {ARXIV_SOFTCOTPP}",
                       font_size=13, color=MUTED).next_to(items, DOWN, buff=0.18)
        self.play(FadeIn(items), FadeIn(credit))
        self.legend = items
        self.credit = credit
        self.wait(1.2)

    # ------------------------------------------------------------------
    # Beat 1 — pure geometry, no architecture yet (rule 1).
    # ------------------------------------------------------------------
    def beat_1_vocab_grid(self):
        cols = [-2.6, -1.3, 0, 1.3, 2.6]
        rows = [1.6, 0.3, -1.0]
        self.grid_dots = VGroup(*[
            Dot(np.array([x, y, 0]), radius=0.055, color=SCRATCH, fill_opacity=0.85)
            for y in rows for x in cols
        ])
        hop_start = np.array([0.0, 1.6, 0])
        hop_end = np.array([1.3, 1.6, 0])
        self.hop_arrow = Arrow(hop_start, hop_end, buff=0.08, color=SCRATCH, stroke_width=5)

        self.caption = SafeText(
            "Every real token lives at a fixed coordinate in embedding space — the vocabulary grid.",
            font_size=25,
        ).to_edge(DOWN, buff=0.4)
        caption2 = SafeText(
            "A discrete chain-of-thought step is a jump: from one grid point to another.",
            font_size=22, color=MUTED,
        ).next_to(self.caption, UP, buff=0.12)
        self.caption_sub = caption2

        self.play(FadeIn(self.grid_dots), FadeIn(self.caption))
        self.wait(1.0)
        self.play(GrowArrow(self.hop_arrow), FadeIn(self.caption_sub))
        self.wait(1.6)

    # ------------------------------------------------------------------
    # Beat 2 — free a point from the grid. Still pure geometry.
    # ------------------------------------------------------------------
    def beat_2_free_point(self):
        new_caption = SafeText(
            "What if a step didn't have to land on the grid?",
            font_size=26,
        ).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "Free a point — it can be anywhere in the continuous space. That's latent reasoning.",
            font_size=22, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        source = self.grid_dots[8]  # the arrival point of the beat-1 hop, at (1.3, 1.6)
        self.soft_dot = Dot(source.get_center(), radius=0.06, color=SCRATCH, fill_opacity=0.9)
        self.add(self.soft_dot)

        target_pos = np.array([0.5, -1.9, 0])
        self.play(
            Transform(self.caption, new_caption),
            Transform(self.caption_sub, new_sub),
            self.grid_dots.animate.set_opacity(0.25),
            self.hop_arrow.animate.set_opacity(0.15),
            self.soft_dot.animate.move_to(target_pos).scale(1.9).set_color(LATENT),
            run_time=1.8,
        )
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)
        label = SafeText("a free (soft) vector", font_size=18, color=LATENT).next_to(self.soft_dot, DOWN, buff=0.2)
        self.soft_label = label
        self.play(FadeIn(label))
        self.wait(1.8)

    # ------------------------------------------------------------------
    # Beat 3 — introduce the architecture: two frozen models.
    # ------------------------------------------------------------------
    def beat_3_two_frozen_models(self):
        new_caption = SafeText("Where does that free vector actually come from?", font_size=26).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "Two models. Dashed outline = frozen: no gradients ever touch these.",
            font_size=22, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        self.assistant_box = frozen_box(np.array([-4.55, 0.6, 0]), 3.0, 2.5, "assistant LM")
        self.backbone_box = frozen_box(np.array([3.55, 0.6, 0]), 3.6, 2.5, "backbone LLM")

        self.play(
            Transform(self.caption, new_caption),
            Transform(self.caption_sub, new_sub),
            FadeOut(self.grid_dots), FadeOut(self.hop_arrow), FadeOut(self.soft_label),
            FadeIn(self.assistant_box), FadeIn(self.backbone_box),
            self.soft_dot.animate.move_to(self.assistant_box.get_top() + DOWN * 0.55).scale(0.55),
            run_time=1.8,
        )
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)
        self.wait(1.6)

    # ------------------------------------------------------------------
    # Beat 4 — assistant receives [instruction, question, N x [UNK]];
    # final-layer hidden states at the [UNK] positions are the raw
    # soft thought, still in the assistant's own space.
    # ------------------------------------------------------------------
    def beat_4_assistant_produces_raw_thought(self):
        new_caption = SafeText(
            "The assistant reads [instruction, question, N x [UNK]].",
            font_size=24,
        ).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "Its final-layer hidden states at exactly those N placeholder positions are the raw soft thought.",
            font_size=20, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        in_chips = VGroup(
            chip("instr.", MUTED), chip("question", MUTED),
            chip("[UNK]", SCRATCH), chip("[UNK]", SCRATCH),
            chip("[UNK]", SCRATCH), chip("[UNK]", SCRATCH),
        ).arrange(RIGHT, buff=0.12).scale(0.85)
        in_chips.move_to(self.assistant_box.get_bottom() + DOWN * 0.55)
        feed_arrow = Arrow(in_chips.get_top(), self.assistant_box.get_bottom(), buff=0.05,
                            color=MUTED, stroke_width=3)

        self.play(FadeOut(self.soft_dot), FadeIn(in_chips), GrowArrow(feed_arrow),
                   Transform(self.caption, new_caption), Transform(self.caption_sub, new_sub))
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)
        self.wait(1.2)

        # Sit just ABOVE the box's top edge (not inside it, over the title
        # text) — these are hidden states leaving the assistant, not a
        # label crowding its name.
        raw_group = VGroup(*[
            Dot(self.assistant_box.get_top() + UP * 0.3 + RIGHT * dx, radius=0.09, color=LATENT)
            for dx in [-0.6, -0.2, 0.2, 0.6]
        ])
        raw_label = SafeText("raw soft thought — assistant space, dim d_assist", font_size=16, color=LATENT)
        raw_label.next_to(raw_group, UP, buff=0.18)

        self.play(FadeIn(raw_group), FadeIn(raw_label))
        self.raw_group = raw_group
        self.raw_label = raw_label
        self.in_chips = in_chips
        self.feed_arrow = feed_arrow
        self.wait(1.8)

    # ------------------------------------------------------------------
    # Beat 5 — dimension mismatch: the single trainable linear layer.
    # New color (TRAIN) introduced here and ONLY here.
    # ------------------------------------------------------------------
    def beat_5_projection_layer(self):
        new_caption = SafeText(
            "The assistant's space and the backbone's space aren't the same size.",
            font_size=24,
        ).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "One trainable linear layer projects assistant-space into backbone-space.",
            font_size=21, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        proj_center = np.array([-0.5, 0.6, 0])
        proj_fill = Rectangle(width=1.5, height=1.1, color=TRAIN, fill_color=TRAIN,
                               fill_opacity=0.22, stroke_width=3).move_to(proj_center)
        proj_label = SafeText("Linear_theta", font_size=18, color=TRAIN, weight=BOLD).move_to(proj_center + UP * 0.2)
        proj_sub = SafeText("R^d_assist -> R^d_LLM", font_size=13, color=TRAIN).move_to(proj_center + DOWN * 0.22)
        proj_note = SafeText("the ONLY trainable parameters", font_size=13, color=TRAIN).next_to(
            VGroup(proj_fill, proj_label, proj_sub), DOWN, buff=0.14)
        # z-index guards against fill_opacity later covering the labels —
        # see frozen_box()/chip() for the same fix applied there.
        proj_fill.set_z_index(0)
        proj_label.set_z_index(2)
        proj_sub.set_z_index(2)
        self.proj_box = VGroup(proj_fill, proj_label, proj_sub)
        self.proj_note = proj_note

        self.play(
            Transform(self.caption, new_caption), Transform(self.caption_sub, new_sub),
            FadeOut(self.in_chips), FadeOut(self.feed_arrow), FadeOut(self.raw_label),
            self.raw_group.animate.move_to(proj_center + LEFT * 0.5).arrange(DOWN, buff=0.12).move_to(proj_center + LEFT * 0.9),
        )
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)
        self.play(FadeIn(self.proj_box), FadeIn(self.proj_note))
        self.wait(1.0)

        projected_group = VGroup(*[
            Dot(proj_center + RIGHT * 1.6 + UP * dy, radius=0.09, color=LATENT, stroke_color=TRAIN, stroke_width=2)
            for dy in [0.36, 0.12, -0.12, -0.36]
        ])
        # NOTE: proj_fill's fill_opacity is deliberately never pushed toward
        # 1 here (or anywhere else in this file) — empirically, a fully
        # opaque fill on this particular Rectangle renders in front of its
        # own label text regardless of z_index, so we keep it translucent
        # and use Indicate (a color/scale pulse) for "activation" emphasis
        # instead of an opacity ramp.
        self.play(
            Transform(self.raw_group, projected_group),
            Indicate(self.proj_box, color=TRAIN, scale_factor=1.08),
            run_time=1.4,
        )
        self.projected_group = self.raw_group
        self.wait(1.6)

    # ------------------------------------------------------------------
    # Beat 6 — splicing: x_LLM = concat[Instruction, Question, T_soft].
    # Backbone decodes reasoning + answer, completely normally. Show
    # L=4-6 soft vectors standing in for ~24 discrete tokens.
    # ------------------------------------------------------------------
    def beat_6_splice_and_decode(self):
        new_caption = SafeText(
            "x_LLM = concat[ Instruction, Question, T_soft ]",
            font_size=24,
        ).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "The frozen backbone decodes reasoning + answer from there, completely normally.",
            font_size=20, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        splice_chips = VGroup(chip("instr.", MUTED), chip("question", MUTED)).arrange(RIGHT, buff=0.12).scale(0.85)
        target_pos = self.backbone_box.get_bottom() + DOWN * 0.55 + LEFT * 0.9
        splice_chips.move_to(target_pos)

        ghost_row = VGroup(*[
            RoundedRectangle(corner_radius=0.04, width=0.28, height=0.28, color=MUTED, stroke_width=1, fill_opacity=0)
            for _ in range(24)
        ]).arrange_in_grid(rows=2, cols=12, buff=0.05)
        ghost_row.scale(0.72).next_to(self.backbone_box, UP, buff=0.35)
        ghost_label = SafeText("~24 discrete CoT tokens (what this replaces)", font_size=14, color=MUTED)
        ghost_label.next_to(ghost_row, UP, buff=0.08)
        ghost_group = VGroup(ghost_row, ghost_label)

        self.play(
            Transform(self.caption, new_caption), Transform(self.caption_sub, new_sub),
            FadeOut(self.proj_note),
            FadeIn(splice_chips),
            self.projected_group.animate.arrange(RIGHT, buff=0.15).move_to(target_pos + RIGHT * 1.5),
            FadeIn(ghost_group, shift=DOWN * 0.2),
        )
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)
        self.wait(1.2)

        compress_label = SafeText("L=4-6 soft vectors  ~=  4-6x compression", font_size=16, color=LATENT)
        compress_label.next_to(self.projected_group, UP, buff=0.25)
        feed = Arrow(target_pos, self.backbone_box.get_bottom(), buff=0.05, color=MUTED, stroke_width=3)

        self.play(FadeIn(compress_label), GrowArrow(feed), FadeOut(ghost_group))

        # Above the box (in the space the ghost row just vacated), not to
        # its right — backbone_box's right edge already sits close to the
        # frame edge, and a row of output chips placed there would clip.
        out_chips = VGroup(*[chip(t, SCRATCH, font_size=14) for t in ["so...", "given", "=>", "42"]])
        out_chips.arrange(RIGHT, buff=0.1).scale(0.85).next_to(self.backbone_box, UP, buff=0.35)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in out_chips], lag_ratio=0.25))
        out_label = SafeText("reasoning + answer, decoded normally", font_size=14, color=SCRATCH).next_to(out_chips, UP, buff=0.12)
        self.play(FadeIn(out_label))

        self.splice_chips = splice_chips
        self.compress_label = compress_label
        self.feed_into_backbone = feed
        self.out_chips = out_chips
        self.out_label = out_label
        self.wait(1.8)

    # ------------------------------------------------------------------
    # Beat 7 — training: gradient flows backward, solid only through
    # the projection layer, blocked at both frozen boundaries.
    # ------------------------------------------------------------------
    def beat_7_gradient_flow(self):
        new_caption = SafeText(
            "Train with standard next-token loss over the reasoning + answer span.",
            font_size=23,
        ).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "Gradients flow backward — solid only through the projection layer.",
            font_size=20, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        clear_group = VGroup(self.out_chips, self.out_label, self.compress_label,
                              self.splice_chips, self.feed_into_backbone, self.projected_group)
        self.play(FadeOut(clear_group), Transform(self.caption, new_caption), Transform(self.caption_sub, new_sub))
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)

        loss_label = SafeText("loss", font_size=16, color=GATE).next_to(self.backbone_box, RIGHT, buff=0.5)
        seg_backbone = DashedLine(
            self.backbone_box.get_left() + RIGHT * 0.1, self.proj_box.get_right() + LEFT * 0.1,
            color=MUTED, stroke_width=4,
        )
        block_1 = SafeText("blocked", font_size=13, color=MUTED).next_to(seg_backbone, UP, buff=0.1)
        seg_proj = Arrow(self.proj_box.get_right(), self.proj_box.get_left(), buff=0.0,
                          color=TRAIN, stroke_width=7)
        seg_assistant = DashedLine(
            self.proj_box.get_left() + LEFT * 0.1, self.assistant_box.get_right() + LEFT * 0.1,
            color=MUTED, stroke_width=4,
        )
        block_2 = SafeText("blocked", font_size=13, color=MUTED).next_to(seg_assistant, UP, buff=0.1)

        self.play(FadeIn(loss_label), Create(seg_backbone), FadeIn(block_1))
        self.play(GrowArrow(seg_proj))
        self.play(Create(seg_assistant), FadeIn(block_2))

        closing = SafeText(
            "The entire trainable surface of the system: one linear layer.",
            font_size=20, color=TRAIN,
        ).next_to(VGroup(self.assistant_box, self.backbone_box), DOWN, buff=0.6)
        self.play(FadeIn(closing))

        # Transient training-only visuals — removed entirely (not just
        # dimmed) before the next beats reuse this same screen space for
        # bar charts and the M-soft-thought picture.
        self.grad_transient = VGroup(loss_label, seg_backbone, block_1, seg_proj, seg_assistant, block_2, closing)
        self.wait(2.4)

    # ------------------------------------------------------------------
    # Beat 8 — first real numbers: SoftCoT vs zero-shot CoT.
    # ------------------------------------------------------------------
    def beat_8_first_numbers(self):
        new_caption = SafeText("First checkpoint, real numbers.", font_size=26).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "LLaMA-3.1-8B-Instruct, avg of 5 benchmarks: GSM8K, ASDiv-Aug, AQuA, StrategyQA, Date-Understanding.",
            font_size=17, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        # The gradient-flow diagram was specific to the training beat — drop
        # it entirely (not just dim it) so it can't ghost behind the bar
        # chart and the beats that follow. The three architecture boxes
        # stay, dimmed, as a light backdrop.
        self.arch_group = VGroup(self.assistant_box, self.backbone_box, self.proj_box)
        self.play(
            FadeOut(self.grad_transient),
            self.arch_group.animate.set_opacity(0.15),
            Transform(self.caption, new_caption), Transform(self.caption_sub, new_sub),
        )
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)

        baseline_y = -0.6
        scale = 0.035
        bar1 = pct_bar(-1.4, 68.21, baseline_y, SCRATCH, scale)
        bar2 = pct_bar(1.4, 70.52, baseline_y, LATENT, scale)
        lbl1 = SafeText("zero-shot CoT\n68.21%", font_size=18, color=SCRATCH, line_spacing=0.9).next_to(bar1, DOWN, buff=0.15)
        lbl2 = SafeText("SoftCoT\n70.52%", font_size=18, color=LATENT, line_spacing=0.9).next_to(bar2, DOWN, buff=0.15)
        axis = Line(np.array([-2.4, baseline_y, 0]), np.array([2.4, baseline_y, 0]), color=MUTED, stroke_width=1)

        self.play(FadeIn(axis), GrowFromEdge(bar1, DOWN), GrowFromEdge(bar2, DOWN), FadeIn(lbl1), FadeIn(lbl2))
        self.bars8 = VGroup(axis, bar1, bar2, lbl1, lbl2)
        self.wait(2.4)

    # ------------------------------------------------------------------
    # Beat 9 — the gap SoftCoT++ closes: this pipeline is deterministic.
    # ------------------------------------------------------------------
    def beat_9_determinism_gap(self):
        new_caption = SafeText(
            "But this pipeline is deterministic per input.",
            font_size=25,
        ).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "Same frozen assistant, same N identical [UNK]s, same soft thought — every time.",
            font_size=20, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        self.play(FadeOut(self.bars8), Transform(self.caption, new_caption), Transform(self.caption_sub, new_sub))
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)

        single_dot = Dot(np.array([-3.0, 0.6, 0]), radius=0.12, color=LATENT)
        single_label = SafeText("one soft thought, always", font_size=16, color=LATENT).next_to(single_dot, DOWN, buff=0.2)
        no_branch = SafeText("no self-consistency possible here", font_size=15, color=MUTED).next_to(single_label, DOWN, buff=0.1)

        root = np.array([2.6, 1.4, 0])
        branches = VGroup(*[
            Line(root, root + np.array([dx, -1.6, 0]), color=SCRATCH, stroke_width=3)
            for dx in [-1.1, -0.4, 0.3, 1.0]
        ])
        branch_dots = VGroup(*[Dot(l.get_end(), radius=0.05, color=SCRATCH) for l in branches])
        branch_label = SafeText("discrete CoT: sample at T>0, get diverse chains,\nmajority-vote (self-consistency)",
                             font_size=15, color=SCRATCH, line_spacing=1.0).next_to(branches, DOWN, buff=0.25)

        self.play(FadeIn(single_dot), FadeIn(single_label), FadeIn(no_branch))
        self.wait(0.8)
        self.play(Create(branches), FadeIn(branch_dots), FadeIn(branch_label))

        self.beat9_group = VGroup(single_dot, single_label, no_branch, branches, branch_dots, branch_label)
        self.wait(2.2)

    # ------------------------------------------------------------------
    # Beat 10 — fix: M distinct [INI]^i tokens -> M different soft
    # thoughts from the SAME frozen, deterministic assistant.
    # ------------------------------------------------------------------
    def beat_10_m_distinct_tokens(self):
        new_caption = SafeText(
            "Fix: M distinct, specialized [INI]^i tokens instead of N identical [UNK]s.",
            font_size=22,
        ).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "Same frozen assistant — but different input identities now produce M different soft thoughts.",
            font_size=19, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        self.play(FadeOut(self.beat9_group), Transform(self.caption, new_caption), Transform(self.caption_sub, new_sub))
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)

        # Assistant box is active again (feeding chips, emitting soft
        # thoughts) — bring it back to full visibility, not just the
        # faint backdrop opacity it was left at after beat 8. proj_box is
        # restored separately and capped well below 1 — see the note in
        # beat_5 on why its fill must stay translucent.
        self.play(
            self.assistant_box.animate.set_opacity(0.95),
            self.backbone_box.animate.set_opacity(0.95),
            self.proj_box.animate.set_opacity(0.4),
        )

        ini_chips = VGroup(*[chip(f"[INI]^{i}", TRAIN, font_size=14) for i in range(1, 5)])
        ini_chips.arrange(RIGHT, buff=0.12).scale(0.85).move_to(self.assistant_box.get_bottom() + DOWN * 0.5)
        self.play(FadeIn(ini_chips))
        self.wait(0.6)

        # Above the box's top edge, not inside it over the title text —
        # same fix as beat_4's raw_group.
        m_group = VGroup(*[
            Dot(self.assistant_box.get_top() + UP * 0.3 + RIGHT * dx, radius=0.09, color=LATENT)
            for dx in [-0.3, -0.1, 0.1, 0.3]
        ])
        m_label = SafeText("T_soft^1 ... T_soft^M — close together, but distinct", font_size=15, color=LATENT)
        m_label.next_to(m_group, UP, buff=0.18)

        self.play(FadeIn(m_group), FadeIn(m_label))
        self.ini_chips = ini_chips
        self.m_group = m_group
        self.m_label = m_label
        self.wait(1.8)

    # ------------------------------------------------------------------
    # Beat 11 — contrastive loss shown as literal repulsion.
    # ------------------------------------------------------------------
    def beat_11_contrastive_repulsion(self):
        new_caption = SafeText(
            "A contrastive loss pushes them apart, explicitly, during training.",
            font_size=23,
        ).to_edge(DOWN, buff=0.4)
        new_sub = SafeText(
            "Literal repulsion in the projected space — beyond what distinct inputs alone give.",
            font_size=19, color=MUTED,
        ).next_to(new_caption, UP, buff=0.12)

        self.play(FadeOut(self.ini_chips), Transform(self.caption, new_caption), Transform(self.caption_sub, new_sub))
        self.caption.become(new_caption)
        self.caption_sub.become(new_sub)

        # m_group now starts just above the box's top edge (~y=2.15) —
        # keep the repulsion spread modest so the highest target stays
        # clear of the legend/credit line near the top of the frame.
        center = self.m_group.get_center()
        targets = [center + np.array([-1.1, 0.45, 0]), center + np.array([1.0, 0.35, 0]),
                   center + np.array([-0.9, -0.75, 0]), center + np.array([1.1, -0.65, 0])]
        self.play(
            *[self.m_group[i].animate.move_to(targets[i]).set_color(GATE) for i in range(4)],
            FadeOut(self.m_label),
            run_time=1.6,
        )

        formula = SafeText(
            "L_cl = -sum_k log[ exp(T_soft^k . T_soft^k) / sum_j exp(T_soft^k . T_soft^j) ]",
            font_size=19, color=GATE,
        ).move_to(np.array([0, -2.1, 0]))
        self.play(FadeIn(formula, shift=UP * 0.15))

        self.repel_group = VGroup(formula)
        self.wait(2.4)

    # ------------------------------------------------------------------
    # Beat 12 — aggregation: M soft thoughts -> M chains -> majority
    # vote. Real numbers again, two model families, plus the
    # orthogonal-scaling closing data point.
    # ------------------------------------------------------------------
    def beat_12_aggregation_and_numbers(self):
        new_caption = SafeText(
            "Each of M soft thoughts -> a full independent chain from the frozen backbone -> majority vote.",
            font_size=19,
        ).to_edge(DOWN, buff=0.4)

        clear_group = VGroup(self.m_group, self.repel_group, self.arch_group)
        self.play(FadeOut(clear_group), FadeOut(self.caption_sub), Transform(self.caption, new_caption))
        self.caption.become(new_caption)
        self.wait(1.4)

        subtitle = SafeText(
            "SoftCoT-SC -> SoftCoT++ (self-consistency baseline vs. test-time-scaled)",
            font_size=18, color=MUTED,
        ).move_to(np.array([0, 2.65, 0]))
        self.play(FadeIn(subtitle))

        # Explicit, non-chained y-coordinates for every element in this
        # stack (bars -> labels -> qwen_overall -> orth callout -> caption)
        # so the block can never accumulate enough next_to() drift to run
        # into the bottom caption, however long a label's text turns out.
        baseline_y = 0.1
        scale = 0.024
        label_y = -0.55

        # LLaMA-3.1-8B: math 81.96 -> 82.64, overall 76.88 -> 77.57
        llama_before_math = pct_bar(-4.6, 81.96, baseline_y, SCRATCH, scale)
        llama_after_math = pct_bar(-3.6, 82.64, baseline_y, LATENT, scale)
        llama_lbl = SafeText("LLaMA-3.1-8B math\n81.96 -> 82.64", font_size=14, color=INK, line_spacing=0.9)
        llama_lbl.move_to(np.array([-4.1, label_y, 0]))

        # Qwen3-8B: math 88.65 -> 90.05
        qwen_before_math = pct_bar(-0.5, 88.65, baseline_y, SCRATCH, scale)
        qwen_after_math = pct_bar(0.5, 90.05, baseline_y, LATENT, scale)
        qwen_lbl = SafeText("Qwen3-8B math\n88.65 -> 90.05", font_size=14, color=INK, line_spacing=0.9)
        qwen_lbl.move_to(np.array([0, label_y, 0]))

        # LLaMA overall: 76.88 -> 77.57
        llama_before_all = pct_bar(3.6, 76.88, baseline_y, SCRATCH, scale)
        llama_after_all = pct_bar(4.6, 77.57, baseline_y, LATENT, scale)
        llama_all_lbl = SafeText("LLaMA overall\n76.88 -> 77.57", font_size=14, color=INK, line_spacing=0.9)
        llama_all_lbl.move_to(np.array([4.1, label_y, 0]))

        axis = Line(np.array([-5.4, baseline_y, 0]), np.array([5.4, baseline_y, 0]), color=MUTED, stroke_width=1)

        all_bars = VGroup(
            llama_before_math, llama_after_math, qwen_before_math, qwen_after_math,
            llama_before_all, llama_after_all,
        )
        all_lbls = VGroup(llama_lbl, qwen_lbl, llama_all_lbl)

        self.play(
            FadeIn(axis),
            *[GrowFromEdge(b, DOWN) for b in all_bars],
            FadeIn(all_lbls),
        )
        self.wait(1.6)

        qwen_overall = SafeText("Qwen3-8B overall: 84.87% -> 85.91%", font_size=16, color=MUTED)
        qwen_overall.move_to(np.array([0, -1.15, 0]))
        self.play(FadeIn(qwen_overall))
        self.wait(1.2)

        orth = SafeText(
            "Orthogonal axes: 10 soft thoughts x 10 chains each = 100 total generations\n"
            "pushed GSM8K from 90.99% to 92.71% (LLaMA-3.1-8B).",
            font_size=16, color=GATE, line_spacing=1.0,
        ).move_to(np.array([0, -1.85, 0]))
        self.play(FadeIn(orth))

        self.beat12_group = VGroup(subtitle, axis, all_bars, all_lbls, qwen_overall, orth)
        self.wait(2.6)

    # ------------------------------------------------------------------
    # Beat 13 — honest limitations, in the authors' own framing.
    # ------------------------------------------------------------------
    def beat_13_limitations(self):
        new_caption = SafeText(
            "A PhD-level treatment shows what's still open, not just the headline deltas.",
            font_size=21,
        ).to_edge(DOWN, buff=0.4)

        self.play(FadeOut(self.beat12_group), Transform(self.caption, new_caption))
        self.caption.become(new_caption)

        title = SafeText("In the authors' own words:", font_size=20, color=INK, weight=BOLD)
        lines = VGroup(
            SafeText("- \"the exploration of the latent thought distribution remains preliminary\"", font_size=18, color=MUTED),
            SafeText("- tested only at 8B-parameter inference scale, fully frozen backbones", font_size=18, color=MUTED),
            SafeText("- no reported wall-clock / latency numbers, despite the token-compression claim", font_size=18, color=MUTED),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        block = VGroup(title, lines).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(ORIGIN)

        self.play(FadeIn(block, shift=UP * 0.2))
        self.beat13_group = block
        self.wait(3.0)

    # ------------------------------------------------------------------
    # Beat 14 — close on the payoff: name T_soft, the tensor with no
    # natural-language decoding. Ties back to index.html's allegory.
    # ------------------------------------------------------------------
    def beat_14_close_on_tsoft(self):
        new_caption = SafeText(
            "Name the opaque tensor precisely.",
            font_size=27,
        ).to_edge(DOWN, buff=0.9)

        self.play(FadeOut(self.beat13_group), Transform(self.caption, new_caption))
        self.caption.become(new_caption)

        grid_dot = Dot(np.array([-2.6, 0.8, 0]), radius=0.09, color=SCRATCH)
        grid_check = SafeText("check", font_size=16, color=SCRATCH).next_to(grid_dot, UP, buff=0.15)
        grid_word = SafeText('"therefore" <- vocabulary lookup', font_size=15, color=MUTED).next_to(grid_dot, DOWN, buff=0.2)

        soft_dot = Dot(np.array([2.2, 0.8, 0]), radius=0.14, color=LATENT)
        soft_q = SafeText("?", font_size=28, color=LATENT, weight=BOLD).next_to(soft_dot, UP, buff=0.12)
        soft_word = SafeText("T_soft  <-  no vocabulary lookup exists", font_size=15, color=LATENT).next_to(soft_dot, DOWN, buff=0.2)

        self.play(
            FadeIn(grid_dot), FadeIn(grid_check), FadeIn(grid_word),
            FadeIn(soft_dot), FadeIn(soft_q), FadeIn(soft_word),
        )
        self.wait(1.6)

        payoff = SafeText(
            "T_soft has no natural-language decoding.\nThat's \"the scratchpad is legible, the latent path isn't\" — at the tensor level.",
            font_size=20, color=INK, line_spacing=1.15,
        ).move_to(np.array([0, -1.3, 0]))
        self.play(FadeIn(payoff, shift=UP * 0.15))
        self.wait(2.4)

        closer = SafeText(
            "companion to examples/latent-reasoning/index.html  ·  SoftCoT " + ARXIV_SOFTCOT +
            "  ·  SoftCoT++ " + ARXIV_SOFTCOTPP,
            font_size=13, color=MUTED,
        ).to_edge(DOWN, buff=0.15)
        self.play(FadeIn(closer))
        self.wait(2.0)
