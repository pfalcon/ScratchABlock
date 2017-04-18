import re


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


def natural_sort_key(s):
    if not isinstance(s, str):
        return s
    arr = re.split("([0-9]+)", s)
    return [int(x) if x.isdigit() else x for x in arr]


def repr_stable_dict(d):
    res = "{"
    comma = False
    for k, v in sorted(d.items()):
        if comma:
            res += ", "
        res += "%r: %r" % (k, v)
        comma = True
    res += "}"
    return res

def repr_stable_set(d):
    if not d:
        return "set()"
    res = "{"
    comma = False
    for k in sorted(list(d), key=lambda x: natural_sort_key(repr(x))):
        if comma:
            res += ", "
        res += "%r" % (k,)
        comma = True
    res += "}"
    return res


def repr_stable_seq(d):
    res = "(" if isinstance(d, tuple) else "["
    comma = False
    for el in d:
        if comma:
            res += ", "
        res += repr_stable(el)
        comma = True
    res += ")" if isinstance(d, tuple) else "]"
    return res


def repr_stable(v):
    if isinstance(v, dict):
        return repr_stable_dict(v)
    elif isinstance(v, set):
        return repr_stable_set(v)
    elif isinstance(v, (list, tuple)):
        return repr_stable_seq(v)
    else:
        return str(v)
