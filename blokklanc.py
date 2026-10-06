import hashlib
import time


# ============================================================
# 1. A BLOKK ADATSZERKEZETE
# ============================================================
#
# A blokklánc alapvető építőeleme a blokk. 
# Minden blokk tartalmazza:
#
#   - index: Hanyadik blokk a láncban.
#   - idobelyeg: Mikor jött létre (másodpercben).
#   - adat: A blokkban tárolt információ (pl. tranzakciók).
#   - elozo_hash: Az előző blokk ujjlenyomata. Ez kapcsolja
#                 össze a láncot!
#   - nonce: Egy véletlen szám, ami a bányászathoz kell.
#   - hash: A jelenlegi blokk saját ujjlenyomata.
#
# ============================================================

class Blokk:
    def __init__(self, index, adat, elozo_hash):
        self.index = index
        self.idobelyeg = time.time()
        self.adat = adat
        self.elozo_hash = elozo_hash
        self.nonce = 0
        self.hash = ""  # Ezt később számoljuk ki


# ============================================================
# 2. HASH (UJJLENYOMAT) KISZÁMÍTÁSA
# ============================================================
#
# A hash egy olyan matematikai függvény, amely bármilyen
# hosszú szövegből egy fix hosszúságú (itt 64 karakteres)
# egyedi azonosítót csinál.
#
# SHA-256 algoritmust használunk.
# Bármilyen apró változás az adatokban teljesen más
# hash-t fog eredményezni.
#
# ============================================================

def hash_kiszamitasa(blokk):
    
    # Összefűzzük a blokk adatait egyetlen szöveggé
    szoveg = (
        str(blokk.index) + 
        str(blokk.idobelyeg) + 
        str(blokk.adat) + 
        str(blokk.elozo_hash) + 
        str(blokk.nonce)
    )
    
    # Bájt formátumra alakítjuk és titkosítjuk
    titkositott = hashlib.sha256(szoveg.encode("utf-8"))
    
    # Visszaadjuk a 16-os számrendszerbeli (hex) alakot
    return titkositott.hexdigest()


# ============================================================
# 3. BÁNYÁSZAT (PROOF OF WORK)
# ============================================================
#
# Ahhoz, hogy egy blokk érvényes legyen, a hash-ének
# bizonyos számú nullával (0) kell kezdődnie.
# 
# Mivel a hash eredményét nem tudjuk előre megjósolni,
# el kell kezdenünk találgatni egy véletlen számot (nonce).
# Minden találgatásnál újraszámoljuk a hash-t, amíg
# meg nem kapjuk a kívánt nullákat az elején.
#
# nehezseg = hány darab 0 kell az elejére.
#
# ============================================================

def banyaszas(blokk, nehezseg):
    
    # A cél egy olyan szöveg, ami 'nehezseg' db nullából áll
    cel = "0" * nehezseg
    
    # Kezdeti hash kiszámítása
    blokk.hash = hash_kiszamitasa(blokk)
    
    # Amíg az első pár karakter nem a cél (pl. "00")
    while blokk.hash[:nehezseg] != cel:
        
        # Próbálkozunk a következő számmal
        blokk.nonce += 1
        blokk.hash = hash_kiszamitasa(blokk)
        
    return blokk


# ============================================================
# 4. A GENEZIS BLOKK
# ============================================================
#
# Minden láncnak el kell indulnia valahonnan.
# A legelső blokkot Genezis blokknak hívjuk.
# Nincs előző blokkja, ezért az elozo_hash értéke "0".
#
# ============================================================

def genezis_blokk_letrehozasa():
    
    elso_blokk = Blokk(0, "Genezis Blokk (A kezdet)", "0")
    
    # A genezis blokkot is le kell bányászni! (Nehézség: 2)
    legyartott_blokk = banyaszas(elso_blokk, 2)
    
    return legyartott_blokk


# ============================================================
# 5. ÚJ BLOKK HOZZÁADÁSA A LÁNCHOZ
# ============================================================
#
# 1. Vesszük a lánc utolsó blokkját.
# 2. Megnézzük a hash-ét.
# 3. Ezt beállítjuk az új blokk "elozo_hash" értékének.
# 4. Kibányásszuk az új blokkot.
# 5. Hozzáadjuk a lánchoz (a listához).
#
# ============================================================

def uj_blokk_hozzaadasa(lanc, nehezseg, adat):
    
    # Az utolsó blokk lekérése a listából
    utolso_blokk = lanc[-1]
    
    # Új blokk sorszáma
    uj_index = utolso_blokk.index + 1
    
    # Létrehozzuk a blokkot, összekötve az előzővel
    uj_blokk = Blokk(uj_index, adat, utolso_blokk.hash)
    
    # Bányászat
    kibanyaszott_blokk = banyaszas(uj_blokk, nehezseg)
    
    # Hozzáadás a lánchoz
    lanc.append(kibanyaszott_blokk)
    
    return lanc


# ============================================================
# 6. A LÁNC SÉRTETLENSÉGÉNEK ELLENŐRZÉSE
# ============================================================
#
# Ha valaki átír egy adatot a lánc közepén, a blokk hash-e
# megváltozik. Mivel a következő blokk hivatkozik erre a
# hash-re, a kapcsolat megszakad, és a lánc érvénytelen lesz.
#
# Végigmegyünk az összes blokkon, és ellenőrizzük a
# hash-eket és az összeköttetéseket.
#
# ============================================================

def lanc_ellenorzese(lanc):
    
    # Az 1-es indextől kezdjük (a Genezis blokk a 0.)
    for i in range(1, len(lanc)):
        aktualis_blokk = lanc[i]
        elozo_blokk = lanc[i - 1]
        
        # 1. Ellenőrzés: A kiszámolt hash egyenlő-e az eltárolttal?
        # Ezzel bukik le, ha valaki átírta az adatot.
        kiszamolt = hash_kiszamitasa(aktualis_blokk)
        
        if aktualis_blokk.hash != kiszamolt:
            print(f"HIBA: A(z) {i}. blokk adatai megváltoztak!")
            return False
            
        # 2. Ellenőrzés: Az aktuális blokk előző hash értéke 
        # tényleg az előző blokk hash-e?
        if aktualis_blokk.elozo_hash != elozo_blokk.hash:
            print(f"HIBA: A lánc megszakadt a(z) {i}. blokknál!")
            return False
            
    return True


# ============================================================
# 7. PROGRAM FUTTATÁSA ÉS TESZTELÉS
# ============================================================

print("=== BLOKKLÁNC DEMÓ ===")
print()

# Bányászat nehézsége (hány nullával kell kezdődnie a hash-nek)
NEHEZSEG = 2

# Létrehozzuk az üres láncot, majd beletesszük a Genezis blokkot
blokklanc = []

print("Genezis blokk létrehozása...")
genezis = genezis_blokk_letrehozasa()
blokklanc.append(genezis)
print("Genezis hash:", genezis.hash)
print()

# Hozzáadjuk a tranzakciókat
print("1. blokk bányászata...")
blokklanc = uj_blokk_hozzaadasa(blokklanc, NEHEZSEG, "Kovács Péter utalt 5000 Ft-ot Szabó Annának.")
print("Hash:", blokklanc[-1].hash)
print()

print("2. blokk bányászata...")
blokklanc = uj_blokk_hozzaadasa(blokklanc, NEHEZSEG, "Szabó Anna kifizette a koleszdíjat: -4000 Ft")
print("Hash:", blokklanc[-1].hash)
print()


# ------------------------------------------------------------
# Érvényesség vizsgálata
# ------------------------------------------------------------

print("Lánc ellenőrzése...")
if lanc_ellenorzese(blokklanc):
    print("Minden rendben, a lánc érvényes és hiteles!")
else:
    print("A lánc manipulált!")

print()


# ------------------------------------------------------------
# Hacker támadás szimulálása
# ------------------------------------------------------------
print("--- HACKER TÁMADÁS! ---")
print("Valaki átírja az 1. blokk tranzakcióját 50000 Ft-ra...")

blokklanc[1].adat = "Kovács Péter utalt 50000 Ft-ot Szabó Annának."

# Ellenőrizzük újra
print("Lánc újbóli ellenőrzése...")
if lanc_ellenorzese(blokklanc):
    print("Minden rendben, a lánc érvényes és hiteles!")
else:
    print("A lánc manipulált! A csalás lelepleződött.")