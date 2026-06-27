import java.awt.Component;
import java.io.*;
import java.sql.*;
import javax.swing.*;

public class ExcelUtils {

    public static boolean exportarQuartosCSV(Component parent) {

        JFileChooser chooser = new JFileChooser();
        chooser.setDialogTitle("Guardar ficheiro CSV");
        chooser.setSelectedFile(new File("quartos_export.csv"));

        int resultado = chooser.showSaveDialog(parent);

        if (resultado != JFileChooser.APPROVE_OPTION) {
            return false;
        }

        File ficheiro = chooser.getSelectedFile();

        try (
                Connection conn = Database.ligar();
                Statement stmt = conn.createStatement();
                ResultSet rs = stmt.executeQuery("SELECT * FROM quartos");
                PrintWriter writer = new PrintWriter(ficheiro)
        ) {
            writer.println("id,numero,tipo,preco,estado");

            while (rs.next()) {
                writer.println(
                        rs.getInt("id") + "," +
                        rs.getString("numero") + "," +
                        rs.getString("tipo") + "," +
                        rs.getDouble("preco") + "," +
                        rs.getString("estado")
                );
            }

            return true;

        } catch (Exception e) {
            JOptionPane.showMessageDialog(parent, "Erro ao exportar: " + e.getMessage());
            return false;
        }
    }

    public static boolean importarQuartosCSV(Component parent) {

        JFileChooser chooser = new JFileChooser();
        chooser.setDialogTitle("Escolher ficheiro CSV para importar");

        int resultado = chooser.showOpenDialog(parent);

        if (resultado != JFileChooser.APPROVE_OPTION) {
            return false;
        }

        File ficheiro = chooser.getSelectedFile();

        try (
                BufferedReader reader = new BufferedReader(new FileReader(ficheiro));
                Connection conn = Database.ligar()
        ) {
            reader.readLine();

            String linha;

            while ((linha = reader.readLine()) != null) {
                String[] dados = linha.split(",");

                PreparedStatement stmt = conn.prepareStatement(
                        "INSERT INTO quartos(numero, tipo, preco, estado) VALUES (?, ?, ?, ?)"
                );

                stmt.setString(1, dados[1]);
                stmt.setString(2, dados[2]);
                stmt.setDouble(3, Double.parseDouble(dados[3]));
                stmt.setString(4, dados[4]);

                stmt.executeUpdate();
            }

            return true;

        } catch (Exception e) {
            JOptionPane.showMessageDialog(parent, "Erro ao importar: " + e.getMessage());
            return false;
        }
    }
}