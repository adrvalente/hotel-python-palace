import java.awt.*;
import java.sql.*;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;

public class QuartosFrame extends JFrame {

    private DefaultTableModel modelo;
    private JTable tabela;

    public QuartosFrame() {
        setTitle("Gestão de Quartos");
        setSize(850, 500);
        setLocationRelativeTo(null);

        modelo = new DefaultTableModel(new String[]{"ID", "Número", "Tipo", "Preço", "Estado"}, 0);
        tabela = new JTable(modelo);

        JTextField numero = new JTextField();
        JTextField tipo = new JTextField();
        JTextField preco = new JTextField();
        JTextField estado = new JTextField();

        JPanel form = new JPanel(new GridLayout(4, 2, 10, 10));
        form.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));

        form.add(new JLabel("Número:"));
        form.add(numero);
        form.add(new JLabel("Tipo:"));
        form.add(tipo);
        form.add(new JLabel("Preço:"));
        form.add(preco);
        form.add(new JLabel("Estado:"));
        form.add(estado);

        JButton adicionar = new JButton("Adicionar");
        JButton remover = new JButton("Remover");

        adicionar.addActionListener(e -> {
            try (Connection conn = Database.ligar()) {
                PreparedStatement stmt = conn.prepareStatement(
                        "INSERT INTO quartos(numero, tipo, preco, estado) VALUES (?, ?, ?, ?)"
                );

                stmt.setString(1, numero.getText());
                stmt.setString(2, tipo.getText());
                stmt.setDouble(3, Double.parseDouble(preco.getText()));
                stmt.setString(4, estado.getText());

                stmt.executeUpdate();

                numero.setText("");
                tipo.setText("");
                preco.setText("");
                estado.setText("");

                carregarDados();

            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Erro ao adicionar quarto: " + ex.getMessage());
            }
        });

        remover.addActionListener(e -> removerSelecionado());

        JPanel botoes = new JPanel();
        botoes.add(adicionar);
        botoes.add(remover);

        add(form, BorderLayout.NORTH);
        add(new JScrollPane(tabela), BorderLayout.CENTER);
        add(botoes, BorderLayout.SOUTH);

        carregarDados();
    }

    private void carregarDados() {
        modelo.setRowCount(0);

        try (Connection conn = Database.ligar();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM quartos")) {

            while (rs.next()) {
                modelo.addRow(new Object[]{
                        rs.getInt("id"),
                        rs.getString("numero"),
                        rs.getString("tipo"),
                        rs.getDouble("preco"),
                        rs.getString("estado")
                });
            }

        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao carregar quartos: " + e.getMessage());
        }
    }

    private void removerSelecionado() {
        int linha = tabela.getSelectedRow();

        if (linha < 0) {
            JOptionPane.showMessageDialog(this, "Seleciona um quarto.");
            return;
        }

        int id = Integer.parseInt(modelo.getValueAt(linha, 0).toString());

        try (Connection conn = Database.ligar()) {
            PreparedStatement stmt = conn.prepareStatement("DELETE FROM quartos WHERE id = ?");
            stmt.setInt(1, id);
            stmt.executeUpdate();

            carregarDados();

        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao remover quarto: " + e.getMessage());
        }
    }
}