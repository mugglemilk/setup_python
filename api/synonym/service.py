from .repository import SynonymRepository


class SynonymService:
    def __init__(self, repo: SynonymRepository):
        self._repo = repo

    def lookup(self, word: str) -> dict:
        syns = self._repo.get_synonyms(word)
        if syns is not None:
            return {"word": word, "synonyms": syns}

        canonical = self._repo.get_canonical(word)
        if canonical is not None:
            all_syns = self._repo.get_synonyms(canonical)
            synonyms = [s for s in all_syns if s != word]
            return {"word": word, "synonyms": [canonical] + synonyms}

        return {"word": word, "synonyms": []}
