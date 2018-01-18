
arch_m = None

# Default bitness if specific arch is not loaded
BITNESS = 32


def load_arch(name):
    global arch_m
    arch_m = __import__("arch_" + name)
    for var in dir(arch_m):
        if var.startswith("__"):
            continue
        globals()[var] = getattr(arch_m, var)


if __name__ == "__main__":
    load_arch("xtensa")
    print(BITNESS)
