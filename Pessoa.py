class Pessoa:
    def __init__(self, cpf : int, nome : str, senha : str):
        self.cpf = cpf
        self.nome = nome
        self.senha = senha
    
    def set_senha(self, senha : str):
        self.senha = senha
    
    def get_senha(self) -> str:
        return self.senha
    
    def get_cpf(self) -> int:
        return self.cpf
    
    def get_nome(self) -> str:
        return self.nome
