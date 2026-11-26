import pytest

from multimind.splitter import TextSplitter


class _BoundedText(str):
    """str that fails the test instead of letting split_text loop forever."""

    def __getitem__(self, key):
        if isinstance(key, slice):
            type(self).slices += 1
            if type(self).slices > 1000:
                raise RuntimeError("split_text is not making progress")
        return str.__getitem__(self, key)


@pytest.fixture(autouse=True)
def _reset_counter():
    _BoundedText.slices = 0


def test_sentence_end_inside_overlap_terminates():
    chunks = TextSplitter(chunk_size=5, overlap=2).split_text(_BoundedText("ab.cdefghij"))
    assert chunks[0] == "ab.cd"
    assert chunks[-1].endswith("j")


def test_realistic_sizes_with_early_sentence_end_terminate():
    text = _BoundedText("Hi. " + "word " * 60)
    chunks = TextSplitter(chunk_size=100, overlap=20).split_text(text)
    assert chunks[0].startswith("Hi.")
    assert all(len(c) <= 100 for c in chunks)
    assert chunks[-1].endswith("word")
