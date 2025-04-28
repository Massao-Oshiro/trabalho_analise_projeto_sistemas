from Pessoa import Pessoa
from random import randint

class Bibliotecario(Pessoa):
    def __init__(self, cpf : int, nome : str, senha : str):
        super().__init__(cpf, nome, senha)
        self.id_bibliotecario = randint(10000, 99999)
    
    def get_id_bibliotecario(self) -> int:
        return self.id_bibliotecario
