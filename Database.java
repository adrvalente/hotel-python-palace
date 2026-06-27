import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class Database {

    private static final String URL = "jdbc:sqlite:hotel.db";

    public static Connection ligar() throws Exception {
        Class.forName("org.sqlite.JDBC");
        return DriverManager.getConnection(URL);
    }

    public static void criarTabelas() {
        try (Connection conn = ligar(); Statement stmt = conn.createStatement()) {

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS quartos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT,
                    tipo TEXT,
                    preco REAL,
                    estado TEXT DEFAULT 'Disponível'
                )
            """);

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    nif TEXT,
                    contacto TEXT
                )
            """);

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS reservas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente TEXT,
                    quarto TEXT,
                    entrada TEXT,
                    saida TEXT
                )
            """);

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS faturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente TEXT,
                    reserva TEXT,
                    valor REAL
                )
            """);

            adicionarColuna(stmt, "quartos", "estado", "TEXT DEFAULT 'Disponível'");
            adicionarColuna(stmt, "clientes", "contacto", "TEXT");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void adicionarColuna(
            Statement stmt,
            String tabela,
            String coluna,
            String tipo
    ) {
        try {
            stmt.execute("ALTER TABLE " + tabela + " ADD COLUMN " + coluna + " " + tipo);
        } catch (Exception ignored) {
            // A coluna já existe
        }
    }
}