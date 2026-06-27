import java.awt.*;
import javax.swing.*;

public class HotelPythonPalaceDashboard extends JFrame {

    public HotelPythonPalaceDashboard() {

        setTitle("Hotel Python Palace - Dashboard");

        // ÍCONE
        ImageIcon icon = new ImageIcon("static/img/favicon-32x32.png");

        setIconImage(icon.getImage());

        // JANELA
        setSize(1000, 650);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        // TOPO
        JPanel topo = new JPanel();
        topo.setBackground(new Color(20, 30, 45));
        topo.setPreferredSize(new Dimension(1000, 90));
        topo.setLayout(new BorderLayout());

        JLabel titulo = new JLabel(
                "Hotel Python Palace - Dashboard",
                icon,
                JLabel.LEFT
        );

        titulo.setForeground(Color.WHITE);
        titulo.setFont(new Font("Arial", Font.BOLD, 28));
        titulo.setIconTextGap(15);
        titulo.setBorder(BorderFactory.createEmptyBorder(20, 30, 20, 20));

        topo.add(titulo, BorderLayout.WEST);

        add(topo, BorderLayout.NORTH);

        // MENU LATERAL
        JPanel menu = new JPanel();
        menu.setBackground(new Color(31, 41, 55));
        menu.setPreferredSize(new Dimension(220, 650));
        menu.setLayout(new GridLayout(8, 1, 10, 10));
        menu.setBorder(BorderFactory.createEmptyBorder(30, 15, 30, 15));

        JButton btnQuartos = criarBotao("Quartos");
        JButton btnClientes = criarBotao("Clientes");
        JButton btnReservas = criarBotao("Reservas");
        JButton btnFaturas = criarBotao("Faturas");
        JButton btnCalendario = criarBotao("Calendário");
        JButton btnImportar = criarBotao("Importar Excel");
        JButton btnExportar = criarBotao("Exportar Excel");
        JButton btnSair = criarBotao("Sair");

        menu.add(btnQuartos);
        menu.add(btnClientes);
        menu.add(btnReservas);
        menu.add(btnFaturas);
        menu.add(btnCalendario);
        menu.add(btnImportar);
        menu.add(btnExportar);
        menu.add(btnSair);

        add(menu, BorderLayout.WEST);

        // CONTEÚDO CENTRAL
        JPanel conteudo = new JPanel();
        conteudo.setBackground(new Color(245, 247, 250));
        conteudo.setLayout(new GridLayout(2, 2, 25, 25));
        conteudo.setBorder(BorderFactory.createEmptyBorder(40, 40, 40, 40));

        conteudo.add(criarCard("Quartos", "Gerir quartos do hotel"));
        conteudo.add(criarCard("Clientes", "Adicionar, editar e remover clientes"));
        conteudo.add(criarCard("Reservas", "Consultar e gerir reservas"));
        conteudo.add(criarCard("Faturação", "Gerar e consultar faturas"));

        add(conteudo, BorderLayout.CENTER);

        // AÇÕES DOS BOTÕES

        btnQuartos.addActionListener(e ->
                new QuartosFrame().setVisible(true)
        );

        btnClientes.addActionListener(e ->
                new ClientesFrame().setVisible(true)
        );

        btnReservas.addActionListener(e ->
                new ReservasFrame().setVisible(true)
        );

        btnFaturas.addActionListener(e ->
                new FaturasFrame().setVisible(true)
        );

        btnCalendario.addActionListener(e ->
                new CalendarioFrame().setVisible(true)
        );

        // EXPORTAR CSV
        btnExportar.addActionListener(e -> {

            boolean exportado = ExcelUtils.exportarQuartosCSV(this);

            if (exportado) {

                JOptionPane.showMessageDialog(
                        this,
                        "Exportação concluída!"
                );
            }
        });

        // IMPORTAR CSV
        btnImportar.addActionListener(e -> {

            boolean importado = ExcelUtils.importarQuartosCSV(this);

            if (importado) {

                JOptionPane.showMessageDialog(
                        this,
                        "Importação concluída!"
                );
            }
        });

        // SAIR
        btnSair.addActionListener(e -> System.exit(0));
    }

    // CRIAR BOTÕES
    private JButton criarBotao(String texto) {

        JButton botao = new JButton(texto);

        botao.setFocusPainted(false);

        botao.setBackground(new Color(59, 130, 246));

        botao.setForeground(Color.WHITE);

        botao.setFont(new Font("Arial", Font.BOLD, 15));

        return botao;
    }

    // CRIAR CARDS
    private JPanel criarCard(String titulo, String descricao) {

        JPanel card = new JPanel();

        card.setBackground(Color.WHITE);

        card.setLayout(new BorderLayout());

        card.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(220, 220, 220)),
                BorderFactory.createEmptyBorder(25, 25, 25, 25)
        ));

        JLabel lblTitulo = new JLabel(titulo);

        lblTitulo.setFont(new Font("Arial", Font.BOLD, 24));

        lblTitulo.setForeground(new Color(31, 41, 55));

        JLabel lblDescricao = new JLabel(descricao);

        lblDescricao.setFont(new Font("Arial", Font.PLAIN, 16));

        lblDescricao.setForeground(new Color(90, 90, 90));

        card.add(lblTitulo, BorderLayout.NORTH);

        card.add(lblDescricao, BorderLayout.CENTER);

        return card;
    }

    // MAIN
    public static void main(String[] args) {

        Database.criarTabelas();

        SwingUtilities.invokeLater(() -> {

            new HotelPythonPalaceDashboard().setVisible(true);

        });
    }
}