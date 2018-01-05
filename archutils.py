from core import REG


def reg_range(prefix, first, last):
    return {REG("%s%d" % (prefix, x)) for x in range(first, last + 1)}


def reg_continuous_subrange(regs, ref_range):
    """Taking regs and ref_range as sorted reg lists, returns initial
    consecutive subrange of regs which is in ref_range. E.g. for
    regs={$a2, $a3, $a5}, ref_range=reg_range($a2, $a7), will return
    {$a2, $a3}. The idea is that ABIs usually call for cosecutive
    allocation of regs, so anything after 'hole' is spurious params /
    returns."""
    res = set()
    for r in sorted(ref_range):
        if r in regs:
            res.add(r)
        else:
            return res
    return res
