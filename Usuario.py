from Pessoa import Pessoa
from Livro import Livro

class Usuario(Pessoa):
    def __init__(self, cpf : int, nome : str, senha : str):
        super().__init__(cpf, nome, senha)
        self.livro_alugado = None
        self.multa = 0
        self.prazo_entrega = 0
    
    def set_prazo(self, prazo : int):
        self.prazo_entrega = prazo

    def set_multa(self, multa : float):
        self.multa = multa
    
    def get_livro_alugado(self) -> Livro:
        return self.livro_alugado
    
    def set_livro_alugado(self, livro : Livro):
        self.livro_alugado = livro
    
    def get_multa(self) -> float:
        return self.multa

    def get_prazo(self) -> int:
        return self.prazo_entrega
