# The Unofficial Guide

**Bhim S. — corpus: `campus_life`**

> How the starter works, and every command you'll need, is in `RUNNING.md`.

---

# Unit 1

## What This Does

This is a retrieval-augmented question answerer over `campus_life`, a corpus of
88 short student-written posts about one university: dining halls, dorms (noise
and laundry), courses, transit, and administrative topics like the printing
quota and parking permits. You ask a plain question — "what are the lunch wait
times at Kestrel Commons?" — and it retrieves the most relevant chunks, answers
using only those documents, and names the file the answer came from. If your
question is not covered by the corpus, a relevance gate refuses it instead of
letting the model guess.

## Chunking Strategy

**Chunk size:** one paragraph (≈85–396 characters; 174 on average), not a fixed
character count.
**Overlap:** none.

Every document in this corpus is short — all 88 are under 550 characters, median
305 — so the starter's 800-character window never splits anything: it stores
each whole post as one chunk. That bundles unrelated facts together. Kestrel
Commons' lunch wait times and its opening hours are two different paragraphs in
one file, and under the 800-char chunker a question about hours retrieves the
wait-time sentence along with it.

So I split on paragraph boundaries instead (`chunker.py::split_documents`), which
turns 88 documents into 173 chunks. Each document's title line is prepended to
every chunk so a chunk names its own subject and can be retrieved on its own —
"Hours are 7:00am to 9:00pm…" becomes "Kestrel Commons\n Hours are 7:00am to
9:00pm…". Any paragraph under 60 characters is merged into its neighbour so a
bare heading never becomes a standalone chunk (the shortest chunk produced is 85
characters). Overlap is zero on purpose: paragraph boundaries already fall
between complete thoughts, so character overlap would only duplicate whole facts
rather than rescue a sentence split across a cut.

## Sample Chunks

All five printed by `python app.py chunks -n 5`, produced by
`chunker.py::split_documents`.

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline
You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_340_exams.txt#1` — produced by: `chunker.py::split_documents`

```
CS 340 Databases — assessment
Start the term project in week three, not week eight; everyone learns this the hard way.
```

**Chunk 3** — source: `course_stat_150_exams.txt#0` — produced by: `chunker.py::split_documents`

```
STAT 150 Applied Statistics — assessment
Three equally weighted midterms, no final. No curve, but the lowest midterm is dropped.
```

**Chunk 4** — source: `housing_aldridge_hall.txt#0` — produced by: `chunker.py::split_documents`

```
Aldridge Hall — what it's actually like
I lived here my sophomore year. Built 1968, renovated 2019. Rooms are doubles with a shared bathroom per floor.
```

**Chunk 5** — source: `housing_morrow_house.txt#3` — produced by: `chunker.py::split_documents`

```
Morrow House — what it's actually like
Laundry costs $1.50 wash, $1.25 dry, coin or card. On noise: loud until about 1am on weekends, no enforced quiet hours.
```

Each chunk carries its document's title and reads as one complete thought — none
is a bare heading, and no sentence is cut across an edge.

## Sample Answer

**Question:** How often does the campus shuttle run on weekdays?

**Answer:**

```
The campus shuttle runs a loop every 20 minutes on weekdays (transit_shuttle.txt).
```

The answer names its source file (`transit_shuttle.txt`), as the grounding
instruction in `generate.py` requires.

**My relevance cutoff:** `0.65` (set in `config.py`, `THRESHOLD`).

I ran my five in-corpus questions and the five in `OUT_OF_SCOPE` through
retrieval and recorded the best (lowest) distance for each. The two groups
separated cleanly — everything in-corpus was at or below 0.47, everything
out-of-corpus at or above 0.82 — so I put the cutoff at 0.65, the midpoint of
that gap, which leaves maximal margin on both sides. Lower distance is better;
0.3 is a close match, 0.9 is unrelated.

| Question | In corpus? | Best distance |
|---|---|---|
| How much printing quota does each student get per semester? | yes | 0.3077 |
| What are the lunch wait times at Kestrel Commons? | yes | 0.1791 |
| How often does the campus shuttle run on weekdays? | yes | 0.1825 |
| Which library floor has power outlets at every seat? | yes | 0.4702 |
| How quiet is Tamsin Court? | yes | 0.3159 |
| What is the capital of Mongolia? | no | 0.8246 |
| How do I change the oil in a diesel engine? | no | 0.9228 |
| Who won the 1994 World Cup? | no | 0.8859 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.8487 |
| How do I write a for loop in Rust? | no | 0.8635 |

In-corpus best distance was 0.47; out-of-corpus best was 0.82. The cutoff at
0.65 sits in the gap: all five in-corpus questions pass, all five out-of-corpus
questions are refused.

## How I Used AI

I authored the acceptance criteria and the chunker myself and tested them in my
own terminal first. I then used AI (Claude) as a reviewer — to re-audit my work
and re-run the tests, looking for gaps I had missed. The two moments below are
where that changed the result.

**1. Chunking strategy.** I read the corpus, saw the posts were short and each
covered several separate facts, and wrote a paragraph-boundary chunker that
prepends each document's title to its chunks. I built and ran it myself
(88 documents became 173 chunks). I then asked Claude to audit it: to re-run the
retrieval distances across my five in-corpus and five out-of-scope questions and
tell me whether the split actually helped. The audit came back with a clean gap —
in-corpus best distances at or below 0.47, out-of-corpus at or above 0.82 — which
confirmed the chunks were retrievable on their own. On the strength of that audit
I set the relevance cutoff at 0.65, the midpoint of the gap.

**2. Acceptance criteria.** I drafted the five criteria with their targets and
reasons before running anything. I then asked Claude to stress-test them — to hunt
for a criterion a wrong answer could still pass. It flagged that criterion 2
("every answer names a source") would be satisfied even if the answer cited the
wrong file. That gap is exactly why I added criterion 5 ("the named source is the
correct source"): I wanted the stronger guarantee that a student following the
citation lands on the right document. The stress-test is what surfaced the
difference between the two.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
