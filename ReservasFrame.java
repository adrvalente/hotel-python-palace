import java.awt.*;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;

public class ReservasFrame extends JFrame {

    public ReservasFrame() {
        setTitle("Gestão de Reservas");
        setSize(900, 500);
        setLocationRelativeTo(null);

        String[] colunas = {"Nº Reserva", "Cliente", "Quarto", "Entrada", "Saída"};
        DefaultTableModel modelo = new DefaultTableModel(colunas, 0);

        JTable tabela = new JTable(modelo);

        JTextField reserva = new JTextField();
        JTextField cliente = new JTextField();
        JTextField quarto = new JTextField();
        JTextField entrada = new JTextField();
        JTextField saida = new JTextField();

        JPanel form = new JPanel(new GridLayout(5, 2, 10, 10));
        form.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));

        form.add(new JLabel("Nº Reserva:"));
        form.add(reserva);
        form.add(new JLabel("Cliente:"));
        form.add(cliente);
        form.add(new JLabel("Quarto:"));
        form.add(quarto);
        form.add(new JLabel("Data Entrada:"));
        form.add(entrada);
        form.add(new JLabel("Data Saída:"));
        form.add(saida);

        JButton adicionar = new JButton("Adicionar");
        JButton remover = new JButton("Remover");

        JPanel botoes = new JPanel();
        botoes.add(adicionar);
        botoes.add(remover);

        adicionar.addActionListener(e -> {
            modelo.addRow(new Object[]{
                    reserva.getText(),
                    cliente.getText(),
                    quarto.getText(),
                    entrada.getText(),
                    saida.getText()
            });

            reserva.setText("");
            cliente.setText("");
            quarto.setText("");
            entrada.setText("");
            saida.setText("");
        });

        remover.addActionListener(e -> {
            int linha = tabela.getSelectedRow();
            if (linha >= 0) {
                modelo.removeRow(linha);
            }
        });

        add(form, BorderLayout.NORTH);
        add(new JScrollPane(tabela), BorderLayout.CENTER);
        add(botoes, BorderLayout.SOUTH);
    }
}