import csv
import os


class SynonymRepository:
    def __init__(self, path: str = None):
        if path is None:
            path = os.path.join(os.path.dirname(__file__), '..', '..', 'merged.csv')
        self._path = os.path.abspath(path)
        self._word_to_syns: dict[str, list[str]] = {}
        self._syn_to_word: dict[str, str] = {}
        self._load()

    def _load(self):
        with open(self._path, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if len(row) < 2:
                    continue
                word = row[0].strip()
                syns = [s.strip() for s in row[1].split('|') if s.strip()]
                self._word_to_syns[word] = syns
                for s in syns:
                    self._syn_to_word[s] = word

    def get_synonyms(self, word: str) -> list[str] | None:
        return self._word_to_syns.get(word)

    def get_canonical(self, word: str) -> str | None:
        return self._syn_to_word.get(word)

    def get_all(self) -> dict[str, list[str]]:
        return self._word_to_syns

    def entry_count(self) -> int:
        return len(self._word_to_syns)
