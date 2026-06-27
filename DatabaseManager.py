import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash


DB_NAME = "hotel.db"
DB_PATH = Path(__file__).resolve().parent / DB_NAME


def ligar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [linha["name"] for linha in cursor.fetchall()]
    return coluna in colunas


def adicionar_coluna(cursor, tabela, coluna, definicao):
    if not coluna_existe(cursor, tabela, coluna):
        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}")
        print(f"Coluna adicionada: {tabela}.{coluna}")


def criar_tabelas():
    with ligar() as conn:
        cursor = conn.cursor()

        # CLIENTES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                nif TEXT UNIQUE NOT NULL,
                contacto TEXT,
                email TEXT
            )
        """)

        # UTILIZADORES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilizadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                tipo TEXT DEFAULT 'admin'
            )
        """)

        # QUARTOS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quartos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                preco REAL NOT NULL,
                estado TEXT DEFAULT 'Disponível',
                capacidade INTEGER,
                camas TEXT,
                amenities TEXT
            )
        """)

        # RESERVAS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                quarto_id INTEGER,
                data_entrada TEXT NOT NULL,
                data_saida TEXT NOT NULL,
                estado TEXT DEFAULT 'Ativa',
                observacoes TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (quarto_id) REFERENCES quartos(id)
            )
        """)

        # FATURAS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reserva_id INTEGER,
                valor REAL NOT NULL,
                data_emissao TEXT NOT NULL,
                estado TEXT DEFAULT 'Emitida',
                FOREIGN KEY (reserva_id) REFERENCES reservas(id)
            )
        """)

        conn.commit()


def atualizar_tabelas_existentes():
    with ligar() as conn:
        cursor = conn.cursor()

        # CLIENTES
        adicionar_coluna(cursor, "clientes", "contacto", "TEXT")
        adicionar_coluna(cursor, "clientes", "email", "TEXT")

        # QUARTOS
        adicionar_coluna(cursor, "quartos", "estado", "TEXT DEFAULT 'Disponível'")
        adicionar_coluna(cursor, "quartos", "capacidade", "INTEGER")
        adicionar_coluna(cursor, "quartos", "camas", "TEXT")
        adicionar_coluna(cursor, "quartos", "amenities", "TEXT")

        # RESERVAS
        adicionar_coluna(cursor, "reservas", "estado", "TEXT DEFAULT 'Ativa'")
        adicionar_coluna(cursor, "reservas", "observacoes", "TEXT")

        # FATURAS
        adicionar_coluna(cursor, "faturas", "estado", "TEXT DEFAULT 'Emitida'")

        conn.commit()


def inserir_dados_iniciais():
    with ligar() as conn:
        cursor = conn.cursor()

        quartos = [
            (
                "101",
                "Quarto Standard",
                80.00,
                "Disponível",
                2,
                "1 cama de casal",
                "Wi-Fi, TV, Pequeno-almoço"
            ),

            (
                "102",
                "Quarto Twin",
                95.00,
                "Disponível",
                2,
                "2 camas individuais",
                "Wi-Fi, Secretária, TV, Ar condicionado"
            ),

            (
                "201",
                "Suite Python Palace",
                180.00,
                "Disponível",
                2,
                "1 cama king size",
                "Wi-Fi, TV, Jacuzzi, Varanda, Room service"
            ),
        ]

        # CRIAR ADMIN
        admin = cursor.execute("""
            SELECT id
            FROM utilizadores
            WHERE username = ?
        """, ("admin",)).fetchone()

        if not admin:
            cursor.execute("""
                INSERT INTO utilizadores
                (username, password_hash, tipo)
                VALUES (?, ?, ?)
            """, (
                "admin",
                generate_password_hash("202605"),
                "admin"
            ))

            print("Utilizador admin criado.")

        # INSERIR QUARTOS
        for quarto in quartos:
            cursor.execute("""
                INSERT OR IGNORE INTO quartos
                (numero, tipo, preco, estado, capacidade, camas, amenities)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, quarto)

        conn.commit()


def mostrar_estrutura():
    with ligar() as conn:
        cursor = conn.cursor()

        tabelas = [
            "clientes",
            "utilizadores",
            "quartos",
            "reservas",
            "faturas"
        ]

        print("\nEstrutura atual da base de dados:\n")

        for tabela in tabelas:
            print(f"--- {tabela.upper()} ---")

            cursor.execute(f"PRAGMA table_info({tabela})")

            for coluna in cursor.fetchall():
                print(f"{coluna['name']} | {coluna['type']}")

            print()


def inicializar_base_dados():
    print("A iniciar uniformização da base de dados...")

    criar_tabelas()
    atualizar_tabelas_existentes()
    inserir_dados_iniciais()
    mostrar_estrutura()

    print("Base de dados uniformizada com sucesso.")


if __name__ == "__main__":
    inicializar_base_dados()