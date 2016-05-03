def pairwise(iterable):
    "For sequence of (a, b, c) yield pairs of (a, b), (b, c), (c, None)."
    prev = Ellipsis
    for it in iterable:
        if prev is not Ellipsis:
            yield (prev, it)
        prev = it
    yield (it, None)
