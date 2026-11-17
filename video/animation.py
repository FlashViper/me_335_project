"""Educational noise-cancellation animation based on MIC1 -> U1 -> U2 -> U3 schematic.

Install: pip install manim
Render:  manim -pqh noise_cancellation_manim.py NoiseCancellationExplainer
For quicker preview: manim -pql noise_cancellation_manim.py NoiseCancellationExplainer

Illustrative waveforms, NOT a SPICE model or validated ANC implementation.
"""
from manim import *
import numpy as np

BG = "#0B1830"
NOISE = "#FF645C"
ANTI = "#45C5FF"
MUSIC = "#F9D65C"
RESULT = "#56E39F"
SOFT = "#C5D4E8"

class NoiseCancellationExplainer(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.opening()
        self.circuit()
        self.wave_cancellation()
        self.music_mix()
        self.closing()

    def heading(self, title, subtitle):
        h = Text(title, font_size=38, weight=BOLD).to_edge(UP, buff=.35)
        s = Text(subtitle, font_size=21, color=SOFT).next_to(h, DOWN, buff=.18)
        self.play(Write(h), FadeIn(s), run_time=.9)
        return VGroup(h, s)

    def opening(self):
        head = self.heading("Active Noise Cancellation", "Inside-earcup microphone • Music preserved")
        earcup = RoundedRectangle(width=3.0, height=3.3, corner_radius=.6, color=SOFT, stroke_width=5)
        earcup.set_fill("#182C4B", opacity=.8).shift(RIGHT*1.7+DOWN*.4)
        speaker = Circle(radius=.65, color=ANTI, stroke_width=5).move_to(earcup.get_center()+RIGHT*.35)
        mic = Dot(earcup.get_center()+LEFT*1.05+UP*.75, radius=.12, color=MUSIC)
        mic_label = Text("MIC1", font_size=22, color=MUSIC).next_to(mic, UP)
        noise_label = Text("Ambient noise", font_size=23, color=NOISE).move_to(LEFT*4.3+UP*.7)
        arrow = Arrow(noise_label.get_right()+RIGHT*.15, mic.get_left()+LEFT*.1, color=NOISE, buff=.12)
        ear_label = Text("Headphone speaker", font_size=20, color=ANTI).next_to(earcup, DOWN)
        self.play(Create(earcup), Create(speaker), FadeIn(mic, mic_label), run_time=1.1)
        self.play(Write(noise_label), GrowArrow(arrow), FadeIn(ear_label))
        self.wait(1)
        self.play(FadeOut(VGroup(head, earcup, speaker, mic, mic_label, noise_label, arrow, ear_label)))

    def circuit(self):
        head = self.heading("Signal Path in Your Schematic", "Conceptual block diagram • Not a measured transfer function")
        blocks = VGroup(*[
            RoundedRectangle(width=2.0, height=1.3, corner_radius=.15, stroke_color=c, stroke_width=3)
            for c in [MUSIC, SOFT, ANTI, RESULT]
        ]).arrange(RIGHT, buff=.72).shift(UP*.25)
        labels = ["MIC1", "U1", "U2", "U3"]
        details = ["In-earcup mic", "Pre-amplifier", "Signal shaping", "Music summing"]
        for i, b in enumerate(blocks):
            txt = VGroup(Text(labels[i], font_size=27, weight=BOLD), Text(details[i], font_size=16, color=SOFT))
            txt.arrange(DOWN, buff=.12).move_to(b)
            b.add(txt)
        arrows = VGroup(*[Arrow(blocks[i].get_right(), blocks[i+1].get_left(), buff=.1, color=WHITE) for i in range(3)])
        self.play(LaggedStart(*[FadeIn(b, scale=.9) for b in blocks], lag_ratio=.2), run_time=1.7)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=.2))
        music_text = Text("Music input (R8)", font_size=22, color=MUSIC).next_to(blocks[3], DOWN, buff=1.0)
        music_arrow = Arrow(music_text.get_top(), blocks[3].get_bottom(), color=MUSIC, buff=.12)
        output_text = Text("To headphone (R12)", font_size=21, color=RESULT).next_to(blocks[3], RIGHT, buff=.48)
        self.play(FadeIn(music_text), GrowArrow(music_arrow), FadeIn(output_text))
        note = Text("Cancellation requires the correct phase and amplitude AT THE EAR.", font_size=20, color=SOFT).to_edge(DOWN, buff=.5)
        self.play(FadeIn(note))
        self.wait(1.7)
        self.play(FadeOut(VGroup(head, blocks, arrows, music_text, music_arrow, output_text, note)))

    def wave_axes(self, y_shift=0):
        ax = Axes(x_range=[0, 4*np.pi, np.pi], y_range=[-1.65, 1.65, .5],
                  x_length=10.6, y_length=4.3, tips=False,
                  axis_config={"color": SOFT, "include_numbers": False}).shift(DOWN*.4 + UP*y_shift)
        return ax

    def wave_cancellation(self):
        head = self.heading("Destructive Interference", "Idealized noise and opposite-phase anti-noise")
        ax = self.wave_axes()
        t = ValueTracker(0)
        noise = always_redraw(lambda: ax.plot(lambda x: np.sin(x-t.get_value()), x_range=[0,4*np.pi,.04], color=NOISE, stroke_width=4))
        anti = always_redraw(lambda: ax.plot(lambda x: -.95*np.sin(x-t.get_value()), x_range=[0,4*np.pi,.04], color=ANTI, stroke_width=4))
        residual = always_redraw(lambda: ax.plot(lambda x: .05*np.sin(x-t.get_value()), x_range=[0,4*np.pi,.04], color=RESULT, stroke_width=5))
        legend = VGroup(*[
            VGroup(Line(ORIGIN, RIGHT*.42, color=c, stroke_width=5), Text(n, font_size=19, color=c)).arrange(RIGHT, buff=.13)
            for c,n in [(NOISE,"Noise at ear"),(ANTI,"Anti-noise at ear"),(RESULT,"Residual noise")]
        ]).arrange(RIGHT, buff=.55).to_edge(DOWN, buff=.35)
        self.play(Create(ax), FadeIn(legend))
        self.play(Create(noise), Create(anti), run_time=1.5)
        self.play(Create(residual))
        self.play(t.animate.set_value(2*np.pi), run_time=5, rate_func=linear)
        self.wait(.5)
        self.play(FadeOut(VGroup(head, ax, noise, anti, residual, legend)))

    def music_mix(self):
        head = self.heading("Music Remains Audible", "At the ear: music + residual background noise")
        ax = self.wave_axes()
        t = ValueTracker(0)
        def music_fn(x, phase):
            return .62*np.sin(.75*x-phase) + .22*np.sin(1.8*x-1.4*phase)
        music = always_redraw(lambda: ax.plot(lambda x: music_fn(x,t.get_value()), x_range=[0,4*np.pi,.04], color=MUSIC, stroke_width=4))
        combined = always_redraw(lambda: ax.plot(lambda x: music_fn(x,t.get_value())+.05*np.sin(x-t.get_value()), x_range=[0,4*np.pi,.04], color=RESULT, stroke_width=4))
        legend = VGroup(*[
            VGroup(Line(ORIGIN, RIGHT*.45, color=c, stroke_width=5), Text(n, font_size=20, color=c)).arrange(RIGHT, buff=.15)
            for c,n in [(MUSIC,"Music"),(RESULT,"Music + residual noise")]
        ]).arrange(RIGHT, buff=.75).to_edge(DOWN, buff=.35)
        self.play(Create(ax), FadeIn(legend))
        self.play(Create(music), Create(combined))
        self.play(t.animate.set_value(2*np.pi), run_time=5, rate_func=linear)
        self.wait(.6)
        self.play(FadeOut(VGroup(head, ax, music, combined, legend)))

    def closing(self):
        title = Text("Design Goal", font_size=43, weight=BOLD)
        line1 = Text("Reduce ambient noise at the listener's ear", font_size=28, color=RESULT)
        line2 = Text("while keeping the music signal audible.", font_size=28, color=MUSIC)
        caveat = Text("Illustration only: actual cancellation needs acoustic testing and phase/gain tuning.",
                      font_size=19, color=SOFT)
        group = VGroup(title,line1,line2,caveat).arrange(DOWN,buff=.45)
        self.play(LaggedStart(*[FadeIn(x, shift=UP*.2) for x in group], lag_ratio=.2))
        self.wait(2.5)