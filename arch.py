
arch_m = None

def load_arch(name):
    global arch_m
    arch_m = __import__("arch_" + name)
    for var in dir(arch_m):
        if var.startswith("__"):
            continue
        globals()[var] = getattr(arch_m, var)


# TODO: Support multiple archs/callconv, load dynamically based on
# user options.
load_arch("xtensa")


if __name__ == "__main__":
    load_arch("xtensa")
    print(BITNESS)
