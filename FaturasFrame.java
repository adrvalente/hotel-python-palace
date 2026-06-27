import java.awt.*;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;

public class FaturasFrame extends JFrame {

    public FaturasFrame() {
        setTitle("Gestão de Faturas");
        setSize(800, 500);
        setLocationRelativeTo(null);

        String[] colunas = {"Nº Fatura", "Cliente", "Reserva", "Valor"};
        DefaultTableModel modelo = new DefaultTableModel(colunas, 0);

        JTable tabela = new JTable(modelo);

        JTextField fatura = new JTextField();
        JTextField cliente = new JTextField();
        JTextField reserva = new JTextField();
        JTextField valor = new JTextField();

        JPanel form = new JPanel(new GridLayout(4, 2, 10, 10));
        form.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));

        form.add(new JLabel("Nº Fatura:"));
        form.add(fatura);
        form.add(new JLabel("Cliente:"));
        form.add(cliente);
        form.add(new JLabel("Reserva:"));
        form.add(reserva);
        form.add(new JLabel("Valor:"));
        form.add(valor);

        JButton gerar = new JButton("Gerar Fatura");
        JButton remover = new JButton("Remover");

        JPanel botoes = new JPanel();
        botoes.add(gerar);
        botoes.add(remover);

        gerar.addActionListener(e -> {
            modelo.addRow(new Object[]{
                    fatura.getText(),
                    cliente.getText(),
                    reserva.getText(),
                    valor.getText()
            });

            fatura.setText("");
            cliente.setText("");
            reserva.setText("");
            valor.setText("");
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