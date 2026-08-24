from abc import ABC, abstractmethod


class SearchEngine(ABC):

    @abstractmethod
    def search(self, query: str) -> list[dict]:
        pass