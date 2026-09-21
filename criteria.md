# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** Four of my five questions ask for a fact that lives in
exactly one document (the printing quota, Kestrel's wait times, the shuttle
frequency, Tamsin's noise level), so retrieval only has to surface that one
paragraph. The fifth — "which library floor has power outlets at every seat" —
names the feature (outlets) rather than the answer (basement) and that detail
sits in the second paragraph of its document, away from the "library hours"
wording most likely to match the query. That is the one I expect to be able to
miss, so I target 4 of 5 rather than 5 of 5.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** I set this at 5 of 5, not 4, because nothing in my pipeline
produces an answer without a source in front of it. `build_prompt` in
generate.py stamps every retrieved chunk with `[from <filename>]`, and the
grounding instruction tells the model to name the file it used. A passing
question therefore always has a filename available to cite; if even one answer
came back without a source, that would be a prompt-adherence failure worth
catching, not an acceptable miss.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** When I measured distances in Milestone 4, my five in-corpus
questions came back at 0.18-0.47 and the five OUT_OF_SCOPE questions at
0.82-0.92 — a clean gap from 0.47 to 0.82 with nothing in between. With the
cutoff at 0.65, all five out-of-corpus questions sit well above it, so I could
have written 5 of 5. I keep the target at "at least 4 of 5" because the gap was
measured on one embedding of five questions; a differently-worded out-of-corpus
question could land nearer the boundary, and I would rather the criterion hold
under that than only under the five I happened to try.

---

## 4. Chunks stand alone as complete thoughts

For at least 4 of 5 sampled chunks, the chunk reads as one complete thought: no
chunk is a bare heading, and no sentence is cut in half at either end.

**Why this target:** My chunker splits on paragraph boundaries and merges any
paragraph under 60 characters into its neighbour, precisely so a heading line
like "Kestrel Commons" never becomes a standalone chunk (the shortest chunk it
produces is 85 characters). Because paragraphs in this corpus already end on
sentence boundaries, a chunk with a sentence sliced across its edge would mean
the split logic is broken, not merely suboptimal — so this is something I should
hit on all five, and 4 of 5 leaves room for one judgement call on what counts as
"complete."

---

## 5. The named source is the correct source

For at least 4 of my 5 answered questions, the source the answer names is the
document that actually contains the fact — not merely that *a* source is named.

**Why this target:** Criterion 2 only checks that a source is present; an answer
could cite the wrong file and still pass it. What I actually care about is that a
student who follows the citation lands on the right document. I target 4 of 5
rather than 5 because several topics in this corpus are covered by near-duplicate
pairs — every dining hall and dorm has both a main post and a "followup," and
laundry costs appear in passing across multiple housing files — so the model can
reasonably cite the followup or a sibling document instead of the primary source
for one question.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
