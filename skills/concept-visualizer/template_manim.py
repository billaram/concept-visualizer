"""
concept-visualizer Manim template — authoring notes
=====================================================
Copy this file, author real beat content following the AUTHOR: comments.
Strip all AUTHOR: comments from the final output file — they are
instructions for the skill, not part of the artifact.

This mirrors template.html's structure so the parallel is obvious:
  - COLORS dict          <-> template.html's --accent / legend swatches
                             (rule 3: fixed color-to-meaning mapping —
                             use the SAME hex values in both templates
                             for a given concept)
  - one beat_N() method   <-> one entry in template.html's `steps` array
    per step in the outline  (rule 2: one metaphor — every beat should
                             transform the SAME Mobjects, not introduce
                             new ones)
  - Transform/.animate    <-> transitionTo()'s ~500ms lerp
    between beats            (rule 4: continuity, not jump-cuts)
  - beat_1() below must draw pure geometry, no MathTex/formula (rule 1)

Render with:
  uv run manim -pql template_manim.py {SceneClassName}   # quick draft
  uv run manim -pqh template_manim.py {SceneClassName}   # final quality

If you don't have a LaTeX distribution installed, avoid MathTex/Tex and
use manim.Text() for any on-screen notation instead — see this repo's
README for details on that tradeoff.
"""

from manim import *

# AUTHOR: pick per concept — keep in sync with template.html's CSS custom
# properties (--accent / --q / --k / etc.) so the HTML and video versions
# of this concept read as the same explanation. Declared once, used
# everywhere; rule 3 (fixed color-to-meaning mapping).
COLORS = {
    "object_a": "#3B62C4",   # AUTHOR: name this after what it means, not its color
    "object_b": "#C4763B",
    "highlight": "#3F8F6E",
    "muted": "#5A6577",
}


# AUTHOR: rename the class to the concept, e.g. `AttentionScores`.
class ConceptTemplate(Scene):
    """AUTHOR: one line — what concept this Scene explains."""

    def construct(self):
        # AUTHOR: legend — declare every held object's color once, up
        # front, before beat_1. Mirrors template.html's .legend block.
        self.show_legend()

        # AUTHOR: one call per beat in the shared outline, in order.
        # Each beat method should end by returning/leaving the Mobjects
        # it introduced in `self` state (e.g. self.vector_a) so the next
        # beat can Transform them rather than creating fresh copies.
        self.beat_1_setup()
        self.beat_2_transform()
        # self.beat_3_...()

    # ------------------------------------------------------------------
    # AUTHOR: implement one method per legend entry / step in the outline.
    # ------------------------------------------------------------------

    def show_legend(self):
        """AUTHOR: small text + colored swatch per held object, top of
        frame, shown once and left on screen (or faded down) for the
        rest of the video — never redefine what a color means later."""
        legend_items = VGroup()
        # AUTHOR: one Dot+Text pair per item in COLORS actually used
        swatch = Dot(color=COLORS["object_a"])
        label = Text("Object A", font_size=24).next_to(swatch, RIGHT, buff=0.15)
        legend_items.add(VGroup(swatch, label))
        legend_items.arrange(RIGHT, buff=0.6).to_edge(UP)
        self.play(FadeIn(legend_items))
        self.legend = legend_items
        self.wait(0.5)

    def beat_1_setup(self):
        """Step 1 — pure geometry, no formula (rule 1).
        AUTHOR: draw the metaphor's starting state."""
        self.object_a = Dot(color=COLORS["object_a"])
        caption = Text(
            "AUTHOR: step 1 caption — geometry only, no equation",
            font_size=28,
        ).to_edge(DOWN)
        self.play(FadeIn(self.object_a), FadeIn(caption))
        self.caption = caption
        self.wait(1)

    def beat_2_transform(self):
        """Step 2 — transform the SAME object from beat 1, don't create
        a new one. AUTHOR: replace this with the real second beat."""
        new_caption = Text("AUTHOR: step 2 caption", font_size=28).to_edge(DOWN)
        self.play(
            self.object_a.animate.shift(RIGHT * 2),
            Transform(self.caption, new_caption),
        )
        self.wait(1)
