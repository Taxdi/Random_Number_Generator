
def lcg(seed, a, c, mod):
    while True:
        seed = (a * seed + c) % mod
        yield seed             # yield à l'instar de return suspend l'exec de le fct renvoie la valeur et sauvegarde son état pour reprendre là où elle s'esr arretée


# test du programme 
gen = lcg(mod = 2**32, a = 1664525, c = 1013904223, seed = 42)
for i in range(10):
    print(next(gen))