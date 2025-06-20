from abc import ABC, abstractmethod

class GameObject(ABC):
    @abstractmethod
    def update(self, model):
        pass