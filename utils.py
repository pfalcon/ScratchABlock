
# We need a stable output to compare with expected patterns. But mark
# places where sorting is optional with 'maybesorted' so it can be
# optimized for "production" runs.
maybesorted = sorted


def pairwise(iterable):
    "For sequence of (a, b, c) yield pairs of (a, b), (b, c), (c, None)."
    prev = Ellipsis
    for it in iterable:
        if prev is not Ellipsis:
            yield (prev, it)
        prev = it
    yield (it, None)


def set_union(*sets):
    # Python's set.union is unfortunately not a class method,
    # but a normal method, [and if used as unbound method],
    # requires at least one argument (set).
    if sets:
        return set.union(*sets)
    return set()


def set_intersection(*sets):
    # Python's set.intersection is unfortunately not a class method,
    # but a normal method, [and if used as unbound method],
    # requires at least one argument (set).
    if sets:
        return set.intersection(*sets)
    return set()
