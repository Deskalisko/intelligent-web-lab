from collections import Counter, defaultdict
import csv
from difflib import get_close_matches
from math import log
from pathlib import Path
import re

DATA = Path(__file__).resolve().parent / "articles.csv"

#POLSKIE STOP-WORDS (słowa pomijane / wypełniacze) - tak jak wczesniej bylo stop words tylko ze z ang:
#i tak samo jak w ang - odrzucamy je, bo występują niemal w każdym tekście i nie niosą wartości wyróżniającej
STOP = {
    "i", "w", "na", "do", "z", "o", "po", "dla", "oraz", "nad", 
    "przed", "że", "się", "jest", "ma", "są", "to", "co", "jak"
}

#PARAMETRY STANDARDOWEGO BM25 (Lucene BM25Similarity):
#K1 (1.2): kontroluje nasycenie częstości (jak szybko rośnie waga przy powtarzaniu słowa)
#B (0.75): siła kary za długość dokumentu (1.0 = pełna kara, 0.0 = brak normalizacji długości)
K1 = 1.2
B = 0.75



#tokenizacja:
#text.lower() - 'Procesor' = 'procesor'
#re.findall(r'[^\W_]+', ...) - słowa z polskimi znakami, pomija kropki, przecinki, spacje
#filtruje: długość > 1 znak i brak w zbiorze STOP
def tokenize(text):
    if not isinstance(text, str):
        return []
    return [
        word for word in re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)
        if len(word) > 1 and word not in STOP
    ]


with DATA.open(encoding="utf-8", newline="") as file:# do csv otwieranie
    documents = [{**row, "id": int(row["id"])} for row in csv.DictReader(file)]

#słownik dokumentów po ID |błyskawiczny podgląd treści
by_id = {doc["id"]: doc for doc in documents}

#jak zbudowac indeks odwrócony (INVERTED INDEX):
#zamiast: dokument -> [słowa] (co wymagałoby czytania wszystkich 40 tekstów przy każdym zapytaniu)
#tworzy sie słowo -> {id_dokumentu: częstość_wystąpień} (posting list)
index = defaultdict(dict)  # token -> {doc_id: frequency (tf)}
lengths = {}               # doc_id -> liczba tokenów w danym artykule

for doc in documents:
    #tytuł i treść w jeden ciąg tekstowy sie łączy
    tokens = tokenize(doc["title"] + " " + doc["text"])
    counts = Counter(tokens)
    lengths[doc["id"]] = sum(counts.values())
    
    #zapisuje do indeksu które słowo wystąpiło w którym dokumencie i ile razy (tf) - bylo juz wczesniej
    for term, frequency in counts.items():
        index[term][doc["id"]] = frequency

#AVGDL (Average Document Length)
#średnia długość artykułu w tokenach w całym korpusie (potrzebna do normalizacji długości w BM25)
AVGDL = sum(lengths.values()) / len(documents) if documents else 1.0


def calculate_idf(term):
    """
    Oblicza Inverse Document Frequency (IDF) według wzoru Lucene BM25:
    IDF = log(1 + (N - df + 0.5) / (df + 0.5))
    gdzie:
    - N: całkowita liczba dokumentów w bazie (40)
    - df: Document Frequency (w ilu dokumentach słowo występuje chociaż raz)
    Rzadkie słowa (np. 'procesor', df=1) mają wysokie IDF.
    Częste słowa (np. 'technologia', df=4) mają niższe IDF.
    """
    posting = index.get(term, {})
    df = len(posting)
    if df == 0:
        return 0.0
    n = len(documents)
    return log(1 + (n - df + 0.5) / (df + 0.5))


def bm25(term, doc_id):
    """
    Oblicza cząstkowy wynik BM25 dla jednego słowa (term) w jednym dokumencie (doc_id).
    Wzór:
      norm = k1 * (1 - b + b * (|D| / avgdl))
      score = idf * (tf * (k1 + 1)) / (tf + norm)
    """
    posting = index.get(term, {})
    tf = posting.get(doc_id, 0)
    if not tf:
        return 0.0
    
    idf = calculate_idf(term)
    #normalizacja długości dokumentu: dłuższe teksty mają większą szansę zawierać słowo przypadkowo,
    #więc norm rośnie i dzieli wynik, lekko faworyzując zwięzłe artykuły
    norm = K1 * (1 - B + B * lengths[doc_id] / AVGDL)
    return idf * tf * (K1 + 1) / (tf + norm)


def search(query, top_k=10, category=None): # szukanie artykułów za pomocą odwroconego indeksu i algorytmu BM25 
    """
    Tokenizuje zapytanie użytkownika - na górze to mamy w funkcji tokenize
    Zbiera kandydatów z posting lists (tylko dokumenty zawierające przynajmniej jedno słowo) - to są zbiory dokumentów
    Opcjonalnie filtruje po kategorii ('source') - if category
    Sumuje punkty BM25 dla wszystkich słów zapytania - to jest suma wkładów BM25 dla każdego słowa zapytania czyli score w pętli for doc_id in candidates ponizej 
    Sortuje malejąco po punktach (a przy remisie rosnąco po ID) - to jest w sorted()
    """
    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k musi być dodatnią liczbą całkowitą")
    
    terms = set(tokenize(query))
    if not terms:
        return []
    

    #candidates = suma zbiorów dokumentów z indeksu dla szukanych słów
    candidates = set().union(*(index.get(term, {}) for term in terms))
    results = []
    
    for doc_id in candidates:
        doc = by_id[doc_id]
        
        #filtr kategorii (jeśli podano)
        if category and doc["source"].casefold() != category.casefold():
            continue
        
        #suma wkładów BM25 dla każdego słowa zapytania
        score = sum(bm25(term, doc_id) for term in terms)
        
        results.append({
            "id": doc_id,
            "title": doc["title"],
            "snippet": doc["text"],
            "category": doc["source"],
            "score": score
        })
    
    #-item['score'] -> malejąco po wyniku punktowym
    #item['id'] -> rosnąco po id artykułu w razie remisu
    results = sorted(results, key=lambda item: (-item["score"], item["id"]))[:top_k]
    
    for result in results:
        result["score"] = round(result["score"], 4) #zaokrąglenie wyniku do 4 miejsc 
        
    return results


def suggest(query): #literówki i podpowiedzi sugerowanych slow
    """
    Dla każdego słowa ( o ktore pytamy w zapytaniu) którego NIE ma w naszym indeksie,
    szukamy najbliższego pasującego słowa w kluczach indeksu (difflib)

    Zwracamy słownik: {błędne_słowo: sugerowane_słowo}.
    """
    matches = {}
    for term in tokenize(query):
        if term not in index:
            close = get_close_matches(term, index.keys(), n=1, cutoff=0.72)
            if close:
                matches[term] = close[0]
    return matches


if __name__ == "__main__":
    print("=" * 60) #zamiast \n - tak jest bardziej czytelnie (INFO DLA KAMILA)
    print(f"Liczba dokumentów: {len(documents)}")
    print(f"Liczba unikalnych haseł w indeksie: {len(index)}")
    print(f"Średnia długość artykułu (AVGDL): {AVGDL:.2f} tokenów")
    print("-" * 60)
    
    # Porównanie IDF słów rzadkich i częstych
    print("Porównanie wartości IDF:")
    for word in ["procesor", "technologia", "laptopów", "urządzenia"]:
        idf_val = calculate_idf(word)
        df_val = len(index.get(word, {}))
        print(f"  - '{word}': DF = {df_val}, IDF = {idf_val:.4f}")
    
    print("-" * 60)
    print("Test wyszukiwania dla frazy 'technologia urządzenia':")
    for r in search("technologia urządzenia", top_k=5):
        print(f"  [ID {r['id']:03d}] BM25: {r['score']:.4f} | {r['category']} | {r['title']}")
        
    print("-" * 60)
    print("Test wyszukiwania dla 'procesor':")
    for r in search("procesor", top_k=3):
        print(f"  [ID {r['id']:03d}] BM25: {r['score']:.4f} | {r['title']}")
        
    print("-" * 60)
    print("Test literówki 'procezor':")
    print(f"  Wynik szukania: {search('procezor')}")
    print(f"  Sugestia: {suggest('procezor')}")
    print("=" * 60)
