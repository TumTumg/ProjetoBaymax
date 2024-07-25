using System;
using System.Windows.Forms;

public partial class Form1 : Form
{
    private FuncoesFalas _funcoesFalas;

    public Form1()
    {
        InitializeComponent();
        _funcoesFalas = new FuncoesFalas();
    }

    private void Form1_Load(object sender, EventArgs e)
    {
        MostrarMenu();
    }

    private void MostrarMenu()
    {
        _funcoesFalas.Falar("Olá, eu sou o Baymax. Escolha uma opção: 1 para funções de fala, 2 para sair.");

        string escolha = Microsoft.VisualBasic.Interaction.InputBox("Digite o número da opção desejada:", "Menu Baymax");

        switch (escolha)
        {
            case "1":
                ExecutarFuncoesDeFala();
                break;
            case "2":
                Application.Exit();
                break;
            default:
                _funcoesFalas.Falar("Opção inválida. Por favor, tente novamente.");
                MostrarMenu();
                break;
        }
    }

    private void ExecutarFuncoesDeFala()
    {
        _funcoesFalas.Falar("Você escolheu funções de fala. Diga algo:");

        string comando = Microsoft.VisualBasic.Interaction.InputBox("Digite o comando:", "Funções de Fala");

        if (comando.ToLower().Contains("como vai"))
        {
            _funcoesFalas.Falar("Estou funcionando bem, obrigado por perguntar!");
        }
        else if (comando.ToLower().Contains("olá"))
        {
            _funcoesFalas.Falar("Olá! Como posso ajudar você hoje?");
        }
        else if (comando.ToLower().Contains("ajuda"))
        {
            _funcoesFalas.Falar("Você pode me pedir para saber mais sobre comandos disponíveis.");
        }
        else if (comando.ToLower().Contains("sair"))
        {
            _funcoesFalas.Falar("Encerrando o programa. Até logo!");
            Application.Exit();
        }
        else
        {
            _funcoesFalas.Falar("Desculpe, não entendi o comando.");
        }

        MostrarMenu();
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing && (components != null))
        {
            components.Dispose();
        }
        base.Dispose(disposing);
    }
}
