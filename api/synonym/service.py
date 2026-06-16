from .repository import SynonymRepository
from api.poem.service import _rhymes, _syllabify #อันนี้เอามาทำ tag แนะนำคำไวพจน์สีเขียวจุดที่ 1

def _is_recommended(source, candidate):#อันนี้เอามาทำ tag แนะนำคำไวพจน์สีเขียวจุดที่ 2
    src_syls = _syllabify(source)
    cand_syls = _syllabify(candidate)
    if not src_syls or not cand_syls:
        return False
    if len(src_syls) != len(cand_syls):
        return False
    return _rhymes(src_syls[-1], cand_syls[-1]) #อันนี้เอามาทำ tag แนะนำคำไวพจน์สีเขียวจุดที่ 2

class SynonymService:
    def __init__(self, repo: SynonymRepository):
        self._repo = repo

    def lookup(self, word: str) -> dict:
        syns = self._repo.get_synonyms(word)
        if syns is not None:
            return {"word": word, "synonyms": syns, "recommended": [s for s in syns if _is_recommended(word, s)]} #อันนี้เอามาทำ tag แนะนำคำไวพจน์สีเขียวจุดที่ 3
            # return {"word": word, "synonyms": syns} 
        canonical = self._repo.get_canonical(word) #อันนี้เอามาทำ tag แนะนำคำไวพจน์สีเขียวจุดที่ 4
    # src_syls = _syllabify(source)
        # canonical = self._repo.get_canonical(word)
        if canonical is not None:
            all_syns = self._repo.get_synonyms(canonical)
            synonyms = [s for s in all_syns if s != word]
            # return {"word": word, "synonyms": [canonical] + synonyms}
            return {"word": word, "synonyms": [canonical] + synonyms, "recommended": [s for s in synonyms if _is_recommended(word, s)]} #อันนี้เอามาทำ tag แนะนำคำไวพจน์สีเขียวจุดที่ 5
        return {"word": word, "synonyms": [], "recommended": []} #อันนี้เอามาทำ tag แนะนำคำไวพจน์สีเขียวจุดที่ 6
        # return {"word": word, "synonyms": []}
