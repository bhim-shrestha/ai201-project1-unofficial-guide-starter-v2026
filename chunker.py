"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


# Milestone 3 chunking constants for campus_life.
#
# Evidence: all 88 documents are under 550 characters (median 305), so the
# starter's 800-char window never splits anything — it stores each whole post as
# one chunk and bundles unrelated facts together (Kestrel Commons' lunch wait
# time and its opening hours end up in the same chunk). But every document has
# 2-5 paragraphs, and each paragraph is one distinct fact. So the natural unit
# here is the paragraph, not a character count.
TITLE_MAX_CHARS = 60     # a first paragraph this short is a heading, not content
MIN_CHUNK_CHARS = 60     # merge a paragraph shorter than this into its neighbour


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Paragraph-boundary chunking for the campus_life corpus.

    For each document:
      1. Split on blank lines into paragraphs.
      2. Treat a short first paragraph (<= TITLE_MAX_CHARS) as the document's
         title and prepend it to every chunk, so each chunk names its subject
         and can be retrieved on its own — "Hours are 7am..." becomes
         "Kestrel Commons\\nHours are 7am...".
      3. Merge any paragraph shorter than MIN_CHUNK_CHARS into the chunk being
         built, so a stray one-line aside never becomes a bare fragment.

    Overlap is zero on purpose: paragraph boundaries already fall between
    complete thoughts, so character overlap would only duplicate whole facts,
    not rescue a sentence split across a cut.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]
        if not paragraphs:
            continue

        title = ""
        body = paragraphs
        if len(paragraphs) > 1 and len(paragraphs[0]) <= TITLE_MAX_CHARS:
            title, body = paragraphs[0], paragraphs[1:]

        prefix = f"{title}\n" if title else ""
        index = 0
        buffer = ""
        for para in body:
            buffer = f"{buffer}\n\n{para}" if buffer else para
            # Keep filling the buffer until it clears the minimum, so short
            # paragraphs attach to their neighbour instead of standing alone.
            if len(buffer) < MIN_CHUNK_CHARS:
                continue
            chunks.append(
                Chunk(
                    text=f"{prefix}{buffer}",
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )
            index += 1
            buffer = ""

        # Flush a trailing short paragraph onto the last chunk of this document
        # rather than dropping it or emitting it as a fragment.
        if buffer:
            if index > 0:
                last = chunks[-1]
                chunks[-1] = Chunk(
                    text=f"{last.text}\n\n{buffer}",
                    source=last.source,
                    index=last.index,
                    produced_by=last.produced_by,
                )
            else:
                chunks.append(
                    Chunk(
                        text=f"{prefix}{buffer}",
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
