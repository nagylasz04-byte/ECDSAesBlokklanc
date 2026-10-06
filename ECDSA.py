import hashlib
import secrets


# ============================================================
# 1. ELLIPTIKUS GÖRBE
# ============================================================
#
# A görbe egyenlete:
#
#       y² = x³ + ax + b (mod p)
#
# ahol:
#   a, b -> a görbe paraméterei
#   p    -> prímszám, a véges test modulusa
#
# Például:
#
#       y² = x³ + 2x + 2 (mod 17)
#
# ============================================================

a = 2
b = 2
p = 17


# A végtelen pontot None értékkel fogjuk jelölni.
VEGTELEN = None


# ============================================================
# 2. PONT ELLENŐRZÉSE
# ============================================================
#
# Megnézzük, hogy egy pont rajta van-e a görbén.
#
# A képlet:
#
#       y² ≡ x³ + ax + b (mod p)
#
# ============================================================

def pont_a_gorben(P):
    if P is VEGTELEN:
        return True

    x, y = P

    bal_oldal = (y * y) % p
    jobb_oldal = (x * x * x + a * x + b) % p

    return bal_oldal == jobb_oldal


# ============================================================
# 3. MODULÁRIS INVERZ
# ============================================================
#
# Nekünk szükségünk van például erre:
#
#       k^(-1) mod p
#
# Ez azt a számot jelenti, amelyre:
#
#       k * k^(-1) ≡ 1 (mod p)
#
# Pythonban erre használhatjuk:
#
#       pow(k, -1, p)
#
# Ez nem elliptikus görbe könyvtár, csak a Python beépített
# egészszám-matematikai művelete.
#
# ============================================================

def modularis_inverz(k, modulo):
    return pow(k, -1, modulo)


# ============================================================
# 4. PONTÖSSZEADÁS
# ============================================================
#
# Két pontot:
#
#       P + Q
#
# szeretnénk kiszámítani.
#
# Különböző pontok esetén:
#
#       λ = (y₂ - y₁) / (x₂ - x₁)
#
# Moduláris aritmetikában az osztás helyett inverzt használunk:
#
#       λ = (y₂ - y₁) * (x₂ - x₁)^(-1) mod p
#
# Ezután:
#
#       x₃ = λ² - x₁ - x₂ mod p
#
#       y₃ = λ(x₁ - x₃) - y₁ mod p
#
# ============================================================

def pont_osszeadas(P, Q):

    # P + végtelen = P
    if P is VEGTELEN:
        return Q

    # Q + végtelen = Q
    if Q is VEGTELEN:
        return P

    x1, y1 = P
    x2, y2 = Q

    # Ha Q az ellentettje P-nek:
    #
    #       P + (-P) = O
    #
    # ahol O a végtelen pont.
    if x1 == x2 and (y1 + y2) % p == 0:
        return VEGTELEN

    # --------------------------------------------------------
    # KÉT KÜLÖNBÖZŐ PONT
    # --------------------------------------------------------

    if P != Q:

        # Meredekségből és pontból egyenes egyenletéből:
        # λ = (y₂ - y₁) / (x₂ - x₁)
        #
        # Az osztást moduláris inverzzel végezzük.

        szamlalo = (y2 - y1) % p
        nevezo = (x2 - x1) % p

        nevezo_inverz = modularis_inverz(nevezo, p)

        lambda_ = (szamlalo * nevezo_inverz) % p

    # --------------------------------------------------------
    # PONT DUPLÁZÁSA
    # --------------------------------------------------------
    #
    # P + P = 2P
    # Parciálisan deriváljuk x és y mentén majd ezt kapjuk:
    #
    # Ilyenkor:
    #       
    #       λ = (3x₁² + a) / (2y₁)
    #
    # vagyis:
    #
    #       λ = (3x₁² + a) * (2y₁)^(-1) mod p

    else:

        # Ha y = 0, akkor az érintő függőleges,
        # ezért az eredmény a végtelen pont.

        if y1 == 0:
            return VEGTELEN

        szamlalo = (3 * x1 * x1 + a) % p
        nevezo = (2 * y1) % p

        nevezo_inverz = modularis_inverz(nevezo, p)

        lambda_ = (szamlalo * nevezo_inverz) % p

    # --------------------------------------------------------
    # ÚJ PONT KISZÁMÍTÁSA
    # --------------------------------------------------------
    # x₃ = λ² - x₁ - x₂
    x3 = (lambda_ * lambda_ - x1 - x2) % p

    # y₃ = λ(x₁ - x₃) - y₁
    y3 = (lambda_ * (x1 - x3) - y1) % p

    return (x3, y3)


# ============================================================
# 5. PONTSZORZÁS
# ============================================================
#
# Azt akarjuk kiszámítani:
#
#       k * P
#
# Például:
#
#       5G = G + G + G + G + G
#
# De ezt nem így számoljuk, mert nagy k esetén nagyon lassú.
#
# Ehelyett Double-and-Add algoritmust használunk.
#
# Például:
#
#       13 = 1101₂
#
# Ezért:
#
#       13G = 8G + 4G + G
#
# A pontokat folyamatosan duplázzuk.
#
# ============================================================

def pont_szorzas(k, P):

    eredmeny = VEGTELEN
    aktualis = P

    while k > 0:

        # Ha k utolsó bitje 1,
        # hozzáadjuk az aktuális pontot.

        if k % 2 == 1:
            eredmeny = pont_osszeadas(eredmeny, aktualis)

        # Duplázás:
        #
        # P -> 2P -> 4P -> 8P -> ...

        aktualis = pont_osszeadas(aktualis, aktualis)

        # Következő bináris bit
        k = k // 2

    return eredmeny


# ============================================================
# 6. GENERÁTORPONT
# ============================================================
#
# A G egy nyilvános, rögzített pont.
#
# Olyan pontot kell választanunk, amely a görbén van.
#
# ============================================================

G = (5, 1)

if not pont_a_gorben(G):
    raise ValueError("G nincs rajta a görbén!")


# ============================================================
# 7. A GENERÁTOR RENDE
# ============================================================
#
# Az n azt jelenti, hogy hányszor kell hozzáadni G-t ahhoz,
# hogy megkapjuk a végtelen pontot:
#
#       nG = O
#
# Az ECDSA-ban a számítások modulo n történnek.
#
# Ennél a kis oktatási példánál ezt egyszerűen megkeressük.
#
# ============================================================

def pont_rendje(P):

    aktualis = P

    for n in range(1, 1000):

        if aktualis is VEGTELEN:
            return n

        aktualis = pont_osszeadas(aktualis, P)

    raise ValueError("Nem sikerült megtalálni a pont rendjét.")


n = pont_rendje(G)


# ============================================================
# 8. HASH KÉSZÍTÉSE
# ============================================================
#
# A dokumentumból SHA-256 segítségével készítünk hash-t.
#
#       z = SHA256(üzenet)
#
# Az eredmény egy nagy egész szám lesz.
#
# ============================================================

def hash_uzenet(uzenet):

    hash_bytes = hashlib.sha256(
        uzenet.encode("utf-8")
    ).digest()

    hash_szam = int.from_bytes(hash_bytes, "big")

    return hash_szam


# ============================================================
# 9. KULCSGENERÁLÁS
# ============================================================
#
# Titkos kulcs:
#
#       d
#
# Publikus kulcs:
#
#       Q = dG
#
# ============================================================

def kulcsgeneralas():

    # Véletlen titkos kulcs
    #
    #       1 <= d < n

    d = secrets.randbelow(n - 1) + 1

    # Publikus kulcs:
    #
    #       Q = d * G

    Q = pont_szorzas(d, G)

    return d, Q


# ============================================================
# 10. ECDSA ALÁÍRÁS
# ============================================================
#
# Az aláírás bemenete:
#
#       z = hash(üzenet)
#       d = titkos kulcs
#       k = egyszer használatos nonce
#
# Először:
#
#       R = kG
#
# Ezután:
#
#       r = x_R mod n
#
# Majd:
#
#       s = k^(-1) * (z + rd) mod n
#
# Az aláírás:
#
#       (r, s)
#
# ============================================================

def alairas(uzenet, d):

    # Üzenet hash-elése
    z = hash_uzenet(uzenet)

    while True:

        # Egyszer használatos nonce.
        #
        # Fontos:
        # valódi ECDSA-ban ennek nagyon jó minőségű
        # véletlenszám-generálásra van szüksége.

        k = secrets.randbelow(n - 1) + 1

        # R = kG

        R = pont_szorzas(k, G)

        if R is VEGTELEN:
            continue

        x_R, y_R = R

        # r = x_R mod n

        r = x_R % n

        if r == 0:
            continue

        # k^(-1) mod n

        k_inverz = modularis_inverz(k, n)

        # s = k^(-1) * (z + r*d) mod n

        s = (k_inverz * (z + r * d)) % n

        if s == 0:
            continue

        # A nonce-ot nem adjuk vissza.
        return r, s


# ============================================================
# 11. ECDSA VERIFIKÁCIÓ
# ============================================================
#
# A hitelesítő rendelkezik:
#
#       z = hash(üzenet)
#       Q = publikus kulcs
#       (r, s) = aláírás
#
# Először ellenőrizzük:
#
#       1 <= r < n
#       1 <= s < n
#
# Ezután:
#
#       w = s^(-1) mod n
#
# majd:
#
#       u₁ = zw mod n
#
#       u₂ = rw mod n
#
# s = k^(-1) * (z + rd) mod n - ból levezetve, k -> * G
# Ezután:
#
#       R' = u₁G + u₂Q
#
# Ha:
#
#       x_R' mod n = r
#
# akkor az aláírás érvényes.
#
# ============================================================

def ellenorzes(uzenet, alairas, Q):

    r, s = alairas

    # Ellenőrzés
    if r <= 0 or r >= n:
        return False

    if s <= 0 or s >= n:
        return False

    # Üzenet hash
    z = hash_uzenet(uzenet)

    # w = s^(-1) mod n

    w = modularis_inverz(s, n)

    # u₁ = zw mod n

    u1 = (z * w) % n

    # u₂ = rw mod n

    u2 = (r * w) % n

    # R' = u₁G + u₂Q

    pont1 = pont_szorzas(u1, G)
    pont2 = pont_szorzas(u2, Q)

    R = pont_osszeadas(pont1, pont2)

    if R is VEGTELEN:
        return False

    x_R, y_R = R

    # Ellenőrzés:
    #
    #       x_R mod n == r

    return (x_R % n) == r


# ============================================================
# 12. PROGRAM FUTTATÁSA
# ============================================================

print("=== ECDSA DEMÓ ===")

print()
print("G generátor:", G)
print("G rendje (n):", n)

# Kulcsgenerálás

d, Q = kulcsgeneralas()

print()
print("Titkos kulcs (d):", d)
print("Publikus kulcs (Q):", Q)

# Üzenet

uzenet = "Ez egy titkosított üzenet."

print()
print("Üzenet:", uzenet)

# Aláírás

alairas_ertek = alairas(uzenet, d)

print()
print("Aláírás (r, s):", alairas_ertek)

# Ellenőrzés

sikeres = ellenorzes(
    uzenet,
    alairas_ertek,
    Q
)

print()
print("Eredeti üzenet ellenőrzése:", sikeres)

# ------------------------------------------------------------
# Próbáljuk megváltoztatni az üzenetet.
# ------------------------------------------------------------

hamis_uzenet = "Ez egy módosított üzenet."

sikeres = ellenorzes(
    hamis_uzenet,
    alairas_ertek,
    Q
)

print()
print("Módosított üzenet ellenőrzése:", sikeres)