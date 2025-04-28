import sqlite3
from datetime import datetime
from Livro import Livro
from Pessoa import Pessoa
from Usuario import Usuario
from Bibliotecario import Bibliotecario

class GerenciadorBancoDados:
    def __init__(self):
        self.conn = sqlite3.connect('biblioteca.db')
        self.cursor = self.conn.cursor()
        self.cadastrar_tabelas()

    def cadastrar_tabelas(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS livros (
                    autor VARCHAR(60),
                    titulo VARCHAR(100) PRIMARY KEY,
                    quantidade INTEGER               
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    cpf INTEGER PRIMARY KEY,
                    nome VARCHAR(60) NOT NULL UNIQUE,
                    senha VARCHAR(30) NOT NULL,
                    titulo_livro_alugado VARCHAR(100),
                    multa FLOAT,
                    prazo_entrega INTEGER,
                    FOREIGN KEY (titulo_livro_alugado) REFERENCES livros(titulo)
                )
            ''')

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bibliotecarios (
                    cpf INTEGER NOT NULL UNIQUE,
                    id_bibliotecario INTEGER PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL UNIQUE,
                    senha VARCHAR(30) NOT NULL
                )     
            ''')

            self.conn.commit()
        except sqlite3.Error as e:
            print(e)
            self.conn.rollback()
    
    def cadastrar_livro(self, livro : Livro):
        self.cursor.execute('''
            SELECT titulo FROM livros WHERE titulo = ?
        ''', (livro.get_titulo(),))

        livro.set_quantidade(livro.get_quantidade() + 1)
        if self.cursor.fetchone():
            self.cursor.execute('''
                UPDATE livros SET quantidade = ? WHERE titulo = ?
            ''', (livro.get_quantidade(), livro.get_titulo()))
            self.conn.commit()
            return
        
        self.cursor.execute('''
            INSERT INTO livros (autor, titulo, quantidade)
            VALUES (?, ?, ?)
        ''', (livro.get_autor(), livro.get_titulo(), livro.get_quantidade()))

        self.conn.commit()

    def cadastrar_pessoa(self, pessoa : Pessoa):
        if isinstance(pessoa, Usuario):
            if self.verificar_cadastro_usuario(usuario=pessoa):
                return
            
            livro_titulo = pessoa.get_livro_alugado().get_titulo() if pessoa.get_livro_alugado() else None
            
            self.cursor.execute('''
                INSERT INTO usuarios (cpf, nome, senha, titulo_livro_alugado, multa, prazo_entrega)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (pessoa.get_cpf(), pessoa.get_nome(), pessoa.get_senha(), livro_titulo, pessoa.get_multa(), pessoa.get_prazo()))
        
        elif isinstance(pessoa, Bibliotecario):
            self.cursor.execute('''
                SELECT id_bibliotecario FROM bibliotecarios WHERE id_bibliotecario = ?
            ''', (pessoa.get_id_bibliotecario(),))

            if self.cursor.fetchone():
                print("Bibliotecario ja cadastrado")
                return
            
            self.cursor.execute('''
                INSERT INTO bibliotecarios (cpf, id_bibliotecario, nome, senha)
                VALUES (?, ?, ?, ?)
            ''', (pessoa.get_cpf(), pessoa.get_id_bibliotecario(), pessoa.get_nome(), pessoa.get_senha()))
        
        self.conn.commit()
            
    def cadastrar_emprestimo_livro(self, usuario : Usuario, titulo : str):
        self.cursor.execute('''
            SELECT cpf FROM usuarios WHERE cpf = ?
        ''', (usuario.get_cpf(),))

        usuario_recuperado = self.cursor.fetchone()

        livro_recuperado = self.buscar_livro(titulo=titulo)
        if not usuario_recuperado or not livro_recuperado:
            print("usuario ou livro nao cadastrados no sistema")
            return

        if livro_recuperado.get_quantidade() <= 0:
            print("livro indisponivel para empréstimo no momento")
            return
        
        if usuario.get_livro_alugado():
            print("usuario deve devolver o livro emprestado antes de emprestar outro")
            return
        
        if usuario.get_multa() > 0:
            print("usuario tem multa no nome dele")
            return

        usuario.set_livro_alugado(livro=livro_recuperado)
        livro_recuperado.set_quantidade(quantidade=livro_recuperado.get_quantidade() - 1)
        data_atual = datetime.now()
        data_atual_segundos = int(data_atual.timestamp())
        prazo = data_atual_segundos + (86400 * 7)
        usuario.set_prazo(prazo)

        self.cursor.execute('''
            UPDATE usuarios SET titulo_livro_alugado = ?, prazo_entrega = ? WHERE cpf = ?
        ''', (titulo, usuario.get_prazo(), usuario.get_cpf()))

        self.cursor.execute('''
            UPDATE livros SET quantidade = ? WHERE titulo = ?
        ''', (livro_recuperado.get_quantidade(), titulo))
        self.conn.commit()

    def buscar_livro(self, titulo : str) -> Livro:
        self.cursor.execute('''
            SELECT * FROM livros WHERE titulo = ? 
        ''', (titulo,))

        livro_recuperado = self.cursor.fetchone()
        if not livro_recuperado:
            return None
        
        livro_recuperado2 = Livro(autor=livro_recuperado[0], titulo=livro_recuperado[1])
        livro_recuperado2.set_quantidade(quantidade=livro_recuperado[2])
        return livro_recuperado2
    
    def registrar_devolucao(self, usuario : Usuario):
        if not self.verificar_cadastro_usuario(usuario=usuario):
            return
        
        if not usuario.get_livro_alugado():
            print("usuario nao tem nenhum livro alugado")
            return
        
        if usuario.get_prazo() > 0:
            self.calcular_multa(usuario=usuario)
            if usuario.get_multa() > 0:
                print("usuario deve pagar multa antes de fazer a devolucao")
                return
        
        livro = self.buscar_livro(titulo=usuario.get_livro_alugado().get_titulo())
        livro.set_quantidade(quantidade=livro.get_quantidade() + 1)
        usuario.set_livro_alugado(livro=None)
        usuario.set_prazo(prazo=0)

        self.cursor.execute('''
            UPDATE usuarios SET titulo_livro_alugado = ?, prazo_entrega = ? WHERE cpf = ?
        ''', (None, usuario.get_prazo(), usuario.get_cpf()))

        self.cursor.execute('''
            UPDATE livros SET quantidade = ? WHERE titulo = ?
        ''', (livro.get_quantidade(), livro.get_titulo()))
        self.conn.commit()        

    
    def calcular_multa(self, usuario : Usuario):
        if not self.verificar_cadastro_usuario(usuario=usuario):
            return
        
        data_atual = datetime.now()
        data_atual_segundos = int(data_atual.timestamp())
        segundos_alem_prazo = data_atual_segundos - usuario.get_prazo()
        if segundos_alem_prazo > 0:
            multa = float(segundos_alem_prazo / 86400)
            usuario.set_multa(multa=multa)
            self.cursor.execute('''
                UPDATE usuarios SET multa = ? WHERE cpf = ?
            ''', (usuario.get_multa(), usuario.get_cpf()))
            self.conn.commit()
        
        else:
            print("dentro do prazo")

    def verificar_cadastro_usuario(self, usuario : Usuario) -> bool:
        self.cursor.execute('''
            SELECT cpf FROM usuarios WHERE cpf = ?
        ''', (usuario.get_cpf(),))

        if not self.cursor.fetchone():
            print("usuario nao cadastrado")
            return False
        
        return True

    def registrar_pagamento_multa(self, usuario : Usuario):
        if not self.verificar_cadastro_usuario(usuario=usuario):
            return
        
        if usuario.get_multa() == 0:
            return
        
        usuario.set_multa(multa=0)
        usuario.set_prazo(prazo=0)
        self.cursor.execute('''
            UPDATE usuarios SET multa = ?, prazo = ? WHERE cpf = ?
        ''', (usuario.get_multa(), usuario.get_prazo(), usuario.get_cpf()))
        self.conn.commit()
        self.registrar_devolucao(usuario=usuario)

gerenciador = GerenciadorBancoDados()