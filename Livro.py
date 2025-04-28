class Livro:
    def __init__(self, autor : str, titulo : str):
        self.autor = autor
        self.titulo = titulo
        self.quantidade = 0

    def set_quantidade(self, quantidade : int):
        self.quantidade = quantidade
    
    def get_autor(self) -> str:
        return self.autor
    
    def get_titulo(self) -> str:
        return self.titulo
    
    def get_quantidade(self) -> int:
        return self.quantidade
