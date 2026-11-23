from search_engine import (
    documents, index, lengths, AVGDL, K1, B,
    calculate_idf, bm25, search, suggest, tokenize
)

if __name__ == "__main__":
    #porownanie z miniindeksem z 4 art (1, 2, 4, 5)
    pelne = sorted(index.get("technologia", {}).keys())
    mini = [i for i in pelne if i in (1, 2, 4, 5)]
    brak = set(pelne) - set(mini)
    print("technologia w mini:", mini, "| w calym:", pelne, "| brakowalo:", brak)

    #roznica miedzy jednym a dwoma slowami
    r1 = search("procesor", top_k=1)
    r2 = search("procesor laptopów", top_k=1)
    print("procesor:", r1[0]["id"], r1[0]["score"])
    print("procesor laptopow:", r2[0]["id"], r2[0]["score"])

    #reczne przeliczenie bm25 dla art 1 i slowa procesor
    tf = index["procesor"][1]
    idf = calculate_idf("procesor")
    norm = K1 * (1 - B + B * lengths[1] / AVGDL)
    czastkowy = idf * tf * (K1 + 1) / (tf + norm)
    print(f"kalkulator: tf={tf}, idf={idf:.3f}, norm={norm:.3f}, score={czastkowy:.3f}")

    #filtr kategorii i literowka
    print("Sport bez filtra:", [(r["id"], r["category"]) for r in search("trening", top_k=2)])
    print("Sport z filtrem:", [(r["id"], r["category"]) for r in search("trening", top_k=2, category="Sport")])
    print("procezor:", search("procezor"), "| sugestia:", suggest("procezor"))

    #porownanie idf slowa rzadkiego i czestego
    print(f"IDF: procesor={calculate_idf('procesor'):.3f} vs technologia={calculate_idf('technologia'):.3f}")

    #wyciecie powtarzalnego zdania redakcyjnego
    szablon = "Technologia i urządzenia będą testowane przez użytkowników."
    art1_tekst = next(d["text"] for d in documents if d["id"] == 1)
    art1_skrocony = art1_tekst.replace(szablon, "").strip()
    nowa_dlugosc = len(tokenize(documents[0]["title"] + " " + art1_skrocony))
    nowy_norm = K1 * (1 - B + B * nowa_dlugosc / AVGDL)
    nowy_score = calculate_idf("procesor") * tf * (K1 + 1) / (tf + nowy_norm)
    print(f"art 1 po usunieciu szablonu: dl={nowa_dlugosc} (bylo {lengths[1]}), wynik wzrasta: {bm25('procesor', 1):.3f} -> {nowy_score:.3f}")

    #brak synonimow w bm25
    print("smartfon:", search("smartfon"))

    #proba wlasna
    print("baterii:", [(r["id"], r["score"]) for r in search("baterii", top_k=1)])
    print("akumulator:", search("akumulator"), suggest("akumulator"))
