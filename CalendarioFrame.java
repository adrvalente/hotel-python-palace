import java.awt.*;
import javax.swing.*;

public class CalendarioFrame extends JFrame {

    public CalendarioFrame() {
        setTitle("Calendário de Reservas");
        setSize(900, 600);
        setLocationRelativeTo(null);

        JPanel painel = new JPanel(new GridLayout(6, 7, 5, 5));
        painel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        String[] diasSemana = {"Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"};

        for (String dia : diasSemana) {
            JLabel label = new JLabel(dia, SwingConstants.CENTER);
            label.setFont(new Font("Arial", Font.BOLD, 16));
            painel.add(label);
        }

        for (int i = 1; i <= 35; i++) {
            JButton dia = new JButton(String.valueOf(i));
            dia.setFont(new Font("Arial", Font.BOLD, 16));

            int numeroDia = i;

            dia.addActionListener(e -> {
                JOptionPane.showMessageDialog(
                        this,
                        "Criar reserva para o dia " + numeroDia,
                        "Nova Reserva",
                        JOptionPane.INFORMATION_MESSAGE
                );
            });

            painel.add(dia);
        }

        add(painel);
    }
}