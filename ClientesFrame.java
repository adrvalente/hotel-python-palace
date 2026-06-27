import java.awt.*;
import java.sql.*;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;

public class ClientesFrame extends JFrame {

    private DefaultTableModel modelo;
    private JTable tabela;

    public ClientesFrame() {
        setTitle("Gestão de Clientes");
        setSize(850, 500);
        setLocationRelativeTo(null);

        modelo = new DefaultTableModel(new String[]{"ID", "Nome", "NIF", "Contacto"}, 0);
        tabela = new JTable(modelo);

        JTextField nome = new JTextField();
        JTextField nif = new JTextField();
        JTextField contacto = new JTextField();

        JPanel form = new JPanel(new GridLayout(3, 2, 10, 10));
        form.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));

        form.add(new JLabel("Nome:"));
        form.add(nome);
        form.add(new JLabel("NIF:"));
        form.add(nif);
        form.add(new JLabel("Contacto:"));
        form.add(contacto);

        JButton adicionar = new JButton("Adicionar");
        JButton remover = new JButton("Remover");

        adicionar.addActionListener(e -> {
            try (Connection conn = Database.ligar()) {
                PreparedStatement stmt = conn.prepareStatement(
                        "INSERT INTO clientes(nome, nif, contacto) VALUES (?, ?, ?)"
                );

                stmt.setString(1, nome.getText());
                stmt.setString(2, nif.getText());
                stmt.setString(3, contacto.getText());

                stmt.executeUpdate();

                nome.setText("");
                nif.setText("");
                contacto.setText("");

                carregarDados();

            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Erro ao adicionar cliente: " + ex.getMessage());
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
             ResultSet rs = stmt.executeQuery("SELECT * FROM clientes")) {

            while (rs.next()) {
                modelo.addRow(new Object[]{
                        rs.getInt("id"),
                        rs.getString("nome"),
                        rs.getString("nif"),
                        rs.getString("contacto")
                });
            }

        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao carregar clientes: " + e.getMessage());
        }
    }

    private void removerSelecionado() {
        int linha = tabela.getSelectedRow();

        if (linha < 0) {
            JOptionPane.showMessageDialog(this, "Seleciona um cliente.");
            return;
        }

        int id = Integer.parseInt(modelo.getValueAt(linha, 0).toString());

        try (Connection conn = Database.ligar()) {
            PreparedStatement stmt = conn.prepareStatement("DELETE FROM clientes WHERE id = ?");
            stmt.setInt(1, id);
            stmt.executeUpdate();

            carregarDados();

        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Erro ao remover cliente: " + e.getMessage());
        }
    }
}