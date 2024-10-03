import flet as ft
import google.generativeai as genai
import pyttsx3  # Biblioteca para transformar texto em fala
import threading
import time
import os


class Inicial:
    def __init__(self, page):
        self.page = page
        self.model = self.initialize_model()
        self.chat = self.model.start_chat(history=[])

        # Instância do TTS em nível de classe
        self.tts_engine = pyttsx3.init()
        if not self.set_voice():
            print("Nenhuma voz masculina encontrada, utilizando a voz padrão.")

        self.page.on_route_change = self.route_change  # Define o callback de mudança de rota

        self.show_notification = True  # Variável para controlar a exibição da notificação

        self.loading_screen()  # Exibe a tela de carregamento

    def loading_screen(self):
        """Exibe a tela de carregamento."""
        image_path = "C:/Users/daniel.zlima1/PycharmProjects/ProjetoBaymax/v4/app/Imagens/BaymaxOlá.png"

        # Verifica se a imagem existe
        if not os.path.isfile(image_path):
            print(f"Erro: A imagem '{image_path}' não foi encontrada.")
            image_content = ft.Text("Imagem não encontrada.", color=ft.colors.RED)  # Mensagem de erro
        else:
            image_content = ft.Image(src=image_path, width=self.page.width, height=self.page.height,
                                     fit=ft.ImageFit.CONTAIN)  # Imagem carregada

        loading_content = ft.Stack(
            [
                # Camada de fundo da imagem
                ft.Container(
                    content=image_content,
                    alignment=ft.alignment.bottom_right,  # Imagem no canto inferior direito
                    expand=True,
                ),
                # Texto de "Seu Assistente Baymax"
                ft.Container(
                    content=ft.Text("Seu Assistente Baymax", size=32, color=ft.colors.WHITE),
                    alignment=ft.alignment.top_center,  # Centraliza no topo
                    margin=ft.margin.only(bottom=80),  # Ajusta a margem para distanciar do topo
                ),
                # Texto de "Acesso Antecipado"
                ft.Container(
                    content=ft.Text("Acesso Antecipado", size=20, color=ft.colors.YELLOW_300),
                    alignment=ft.alignment.bottom_left,  # Posiciona no canto inferior esquerdo
                    margin=ft.margin.only(left=20, bottom=20),  # Ajusta a margem para distanciar do canto
                ),
            ]
        )

        # Configura a página com a tela de carregamento
        self.page.views.append(
            ft.View(
                "/loading",
                [
                    ft.Container(
                        content=loading_content,
                        bgcolor=ft.colors.RED,
                        width=self.page.width,
                        height=self.page.height,
                    ),
                ],
            )
        )
        self.page.update()

        # Aguarda 5 segundos antes de carregar a página inicial
        threading.Thread(target=self.delay_loading).start()

    def delay_loading(self):
        """Aguarda um tempo antes de carregar a página inicial."""
        threading.Event().wait(5)  # Aguardando 5 segundos
        self.page.go("/")  # Carrega a página inicial

    def set_voice(self):
        """Configura uma voz masculina para o motor de texto para fala (TTS)."""
        voices = self.tts_engine.getProperty('voices')
        for voice in voices:
            if "male" in voice.name.lower():  # Verifica se a voz é masculina
                self.tts_engine.setProperty('voice', voice.id)
                return True
        return False  # Retorna False se não encontrou uma voz masculina

    def initialize_model(self):
        """Configura o modelo de IA com a API do Gemini."""
        genai.configure(api_key="AIzaSyCk-u-JNCWlX0-G5omIdhictzVNW8bEZbM")  # Substitua pela sua chave API real

        # Configuração do modelo
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "max_output_tokens": 1024,
                "response_mime_type": "text/plain",
            },
            system_instruction="Baymax: Assistente Virtual e Sistema de Gestão de Campus\n"
                
                "Seus Criadores:\n"
                "Daniel Zambotti Lima, Pedro Henrique Nogueira e Vitor Cavallini são seus criadores."
                "Eles custumam estar no quarto andar na sala 407 lab de informática, e no primeiro andar, apelidada a sala como 'Borracharia', sala 106"
                               
                
                "Visão Geral\n"
                "Baymax é um assistente virtual multifuncional desenvolvido para atuar como um hub central de informações e um sistema de gestão para o campus. Com uma interface amigável e suporte avançado para interações por voz, Baymax não só orienta visitantes, mas também gerencia um vasto banco de dados com informações detalhadas sobre o campus, incluindo salas, cursos, professores, eventos e recursos disponíveis.\n\n"
 
                "Funcionalidades Principais\n"
                "Banco de Dados Completo do Campus\n"
                "Baymax funciona como um banco de dados centralizado que armazena e gerencia informações críticas sobre o campus. Este banco de dados pode ser consultado tanto por visitantes quanto por administradores, oferecendo um sistema de gestão eficiente e acessível.\n\n"
 
                "Estrutura do Banco de Dados\n"
                "Salas e Instalações:\n"
                "Nome da Sala: Identificador único de cada sala.\n"
                "Andar: Localização dentro do edifício.\n"
                "Capacidade: Quantidade de pessoas que a sala pode acomodar.\n"
                "Equipamentos Disponíveis: Projetores, computadores, sistema de som, etc.\n"
                "Uso Atual: Informações sobre o curso ou evento em andamento.\n"
 
                "Aqui está a lista de salas disponíveis no campus:\n"
                "5º Andar:\n"
                " - Salas 501 a 507:\n"
                "   - Sala 506: Bar / Cozinha Experimental\n"
                "   - Sala 507: Cozinha Pedagógica\n"
                "4º Andar:\n"
                " - Salas 401 a 408:\n"
                "   - Sala 402: Lab. Design de Interiores\n"
                "   - Sala 403: Lab. Rádio\n"
                "   - Sala 404: Lab. Informática\n"
                "   - Sala 405: Lab. Vídeo\n"
                "   - Salas 406 e 407: Lab. Informática\n"
                "3º Andar:\n"
                " - Salas 301 a 306:\n"
                "   - Sala 303: Manicure / Pedicure\n"
                "   - Sala 304: Moda / Turismo\n"
                "   - Sala 305: Farmácia / Enfermagem / Meio Ambiente\n"
                "   - Sala 306: Beleza / Visagismo\n"
                "2º Andar:\n"
                " - Salas 201 a 212:\n"
                "   - Sala 201: Lab. Informática\n"
                "1º Andar:\n"
                " - Salas 101 a 107:\n"
                "   - Sala 107: LabSenac\n"
                "Térreo:\n"
                " - Atendimento ao Cliente\n"
                " - Secretaria / Administração\n"
                " - Acesso pela Av. Senator Vergueiro\n"
                "1º Subsolo:\n"
                " - Estacionamento\n"
                " - Serviços\n"
                "2º Subsolo:\n"
                " - Biblioteca\n"
                " - Docentes\n"
                "3º Subsolo:\n"
                " - Auditório\n"
                " - Acesso pela Av. Alaino Inoto\n\n"
 
                "Cursos Oferecidos:\n"
                "Nome do Curso: Identificador do curso.\n"
                "Área: Categoria do curso (ex.: Tecnologia, Saúde, Artes, etc.).\n"
                "Duração: Tempo de duração do curso (em horas ou meses).\n"
                "Pré-requisitos: Qualificações necessárias para inscrição.\n"
                "Professores: Lista de professores associados ao curso.\n"
 
                "Professores e Funcionários:\n"
                "Professores de TI: Allan Sobral, geralmente fica na sala 406, e Ualace Lugo, que fica quase sempre na 'Borracharia'"
                "Nome do Professor/Funcionário: Identificador da pessoa.\n"
                "Departamento: Setor ao qual o professor/funcionário pertence.\n"
                "Horários de Atendimento: Horários em que estão disponíveis para consultas.\n"
                "Contato: Informações de contato como email e telefone.\n"
 
                "Eventos e Atividades:\n"
                "Nome do Evento: Identificador do evento.\n"
                "Data e Hora: Data e horário de início e término.\n"
                "Localização: Sala ou área do campus onde o evento acontecerá.\n"
                "Descrição: Breve descrição do evento.\n"
                "Público-Alvo: Grupo de pessoas para quem o evento é destinado (ex.: Alunos, Professores, Aberto ao Público, etc.).\n"
 
                "Orientação e Navegação no Campus\n"
                "Navegação Precisa: Baymax orienta visitantes e estudantes pelo campus, oferecendo direções detalhadas baseadas em mapas digitalizados e informações em tempo real sobre a ocupação das salas e disponibilidade de instalações.\n"
                "Tecnologias Integradas:\n"
                "GPS e Mapas Digitais: Navegação detalhada com base em mapas atualizados do campus.\n"
                "Reconhecimento de Voz: Recebe comandos de voz e oferece direções com feedback em tempo real.\n"
 
                "Interação por Voz\n"
                "Processamento de Comandos: Baymax responde a comandos de voz de maneira natural, entendendo e executando solicitações como \"Onde está a Sala 306?\" ou \"Quais cursos de Tecnologia estão disponíveis atualmente?\".\n"
                "Conversão de Texto em Fala: Baymax responde verbalmente, proporcionando uma experiência interativa e acessível a todos os usuários, incluindo aqueles com necessidades especiais.\n"
 
                "Recuperação e Pesquisa de Informações\n"
                "Busca Otimizada: Baymax utiliza APIs para realizar pesquisas em motores de busca como Google e Bing, oferecendo resultados personalizados de acordo com as necessidades dos usuários.\n"
                "Acesso Rápido a Informações: Baymax pode abrir páginas web relevantes diretamente em seu display ou em dispositivos conectados, facilitando o acesso a informações específicas.\n"
 
                "Gestão de Eventos e Cursos\n"
                "Calendário de Eventos: Baymax gerencia um calendário centralizado de eventos do campus, permitindo que os usuários consultem rapidamente informações sobre palestras, workshops, feiras, entre outros.\n"
                "Informações de Curso: Os alunos podem consultar informações detalhadas sobre os cursos, incluindo horários, professores, conteúdo programático e requisitos de inscrição.\n"
 
                "Medidas de Segurança\n"
                "Proteção Contra SQL Injection: Baymax implementa técnicas avançadas de segurança para proteger seu banco de dados contra ataques maliciosos, garantindo a integridade dos dados.\n"
                "Monitoramento Contínuo: Baymax monitora constantemente o tráfego de dados, prevenindo e reagindo a possíveis ameaças.\n"
 
                "Configuração do Sistema\n"
                "Banco de Dados MySQL:\n"
                "Host: localhost\n"
                "Nome do Banco de Dados: gestao_campus\n"
                "Tabelas Principais: Salas, Cursos, Professores, Eventos, Visitantes\n"
                "Usuário: root\n"
                "Senha: (configurada pelo administrador)\n"
 
                "API Integração: Integra-se com diversas APIs gratuitas para atualização de dados, como APIs de clima para fornecer informações meteorológicas em tempo real ou APIs de transporte para fornecer horários de ônibus e metrôs.\n"
 
                "Cenários de Uso\n"
                "Orientação e Navegação\n"
                "Exemplo: Um visitante pergunta ao Baymax como chegar à Sala 404. Baymax consulta o banco de dados, verifica o mapa digitalizado, e fornece direções detalhadas, considerando até mesmo a ocupação atual das salas para sugerir o caminho mais rápido.\n"
 
                "Consulta de Cursos e Professores\n"
                "Exemplo: Um aluno deseja saber quais cursos de Design estão disponíveis. Baymax consulta a tabela de cursos, filtra os resultados pela área de interesse e apresenta informações detalhadas, incluindo horários, professores e pré-requisitos.\n"
 
                "Gerenciamento e Consulta de Eventos\n"
                "Exemplo: Um professor precisa registrar um novo evento no campus. Baymax permite o cadastro direto do evento no banco de dados, atualizando o calendário do campus e notificando os alunos interessados.\n"
 
                "Monitoramento de Segurança\n"
                "Exemplo: Baymax detecta uma tentativa de acesso não autorizado ao banco de dados. Imediatamente, ativa protocolos de segurança, restringindo o acesso e notificando os administradores do sistema.\n"
 
                "Atributos Distintivos\n"
                "Todos os códigos do GTA San Andreas são emitidos diretamente pelo nosso banco de dados!\n"
                "Estatísticas detalhadas sobre o uso das instalações do campus.\n"
                "Feedback contínuo dos usuários para otimizar a experiência no campus.\n"
                # Substitua pela string correta de configuração do sistema
        )
        return model

    def route_change(self, route_event_or_str):
        """Atualiza a view de acordo com a rota."""
        self.page.views.clear()  # Limpa as views atuais
        route = route_event_or_str.route if hasattr(route_event_or_str, 'route') else route_event_or_str
        views = {
            "/": self.build_home_view,
            "/chatIAFlet": self.build_chat_view,
            "/sobre": self.build_about_view,
            "/contato": self.build_contact_view,
        }
        view_function = views.get(route, self.build_error_view)
        view_function()  # Chama a função de view correspondente
        self.page.update()  # Atualiza a página

    def build_home_view(self):
        """Constrói a página inicial."""
        self.page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Seu Assistente Baymax"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.NavigationBar(
                        destinations=[
                            ft.NavigationBarDestination(icon=ft.icons.CHAT, label="Chat IA"),
                            ft.NavigationBarDestination(icon=ft.icons.INFO, label="Sobre Nós"),
                            ft.NavigationBarDestination(icon=ft.icons.CONTACT_MAIL, label="Contato"),
                            ft.NavigationBarDestination(icon=ft.icons.EXIT_TO_APP, label="Sair"),
                        ],
                        on_change=self.handle_navigation,
                    ),
                    ft.Text("Bem-vindo ao Assistente Baymax!", size=24),
                ],
            )
        )
        self.page.update()  # Atualiza a página

        if self.show_notification:
            self.show_welcome_notification("Usuário")  # Exibe notificação de boas-vindas

    def show_welcome_notification(self, usuario):
        """Exibe uma notificação de boas-vindas ao usuário."""
        notification_text = (
            f"Bem-vindo {usuario}!\n"
            "---Novidades!---\n"
            "- Apresentamos o chat IA\n"
            "- Novas Funcionalidades!\n"
            "- Correção de bugs\n"
            "- Suporte ao usuário\n"
            "- Promoção à saúde\n"
            "- Biblioteca Senac\n"
            "- Auxílio em eventos\n"
            "-----//-----\n"
            "Por que você mesmo não dá uma olhada?"
        )

        # Criação do diálogo
        self.dialog = ft.AlertDialog(
            modal=False,  # Agora é um diálogo não modal
            title=ft.Text("Bem-vindo!"),
            content=ft.Container(
                content=ft.Text(notification_text),
                padding=20,
                width=400,
                height=300,
                bgcolor=ft.colors.GREY_200,  # Cor de fundo cinza claro
                border_radius=ft.BorderRadius(10, 10, 10, 10),  # Raio de borda
                alignment=ft.alignment.center,
            ),
            actions=[
                ft.Checkbox(label="Não mostrar novamente", on_change=self.no_show_again),
                ft.ElevatedButton("Fechar", on_click=self.close_dialog),  # Atualizado para o método close_dialog
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.page.overlay.append(self.dialog)  # Atualizando para usar overlay
        self.dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Ação para fechar o diálogo."""
        print("Fechar clicado!")
        self.page.overlay.remove(self.dialog)  # Remove o diálogo da tela
        self.page.update()  # Atualiza a página

    def no_show_again(self, e):
        """Ação para o checkbox 'Não mostrar novamente'."""
        self.show_notification = not e.control.value  # Atualiza a variável com base no estado do checkbox

    def handle_navigation(self, e):
        """Navega entre diferentes views com base na escolha do usuário."""
        if e.control.selected_index == 0:  # Chat IA
            self.page.route = "/chatIAFlet"
        elif e.control.selected_index == 1:  # Sobre Nós
            self.page.route = "/sobre"
        elif e.control.selected_index == 2:  # Contato
            self.page.route = "/contato"
        else:  # Sair
            self.page.close()

        self.route_change(self.page.route)  # Atualiza a rota

    def build_chat_view(self):
        # Layout de chat com uma caixa de entrada de mensagens e o histórico de conversas
        self.chat_box = ft.Column(scroll="auto", expand=True, alignment=ft.MainAxisAlignment.START, spacing=10)
        self.message_input = ft.TextField(hint_text="Digite sua mensagem...", expand=True, on_submit=self.send_message)

        self.page.views.append(
            ft.View(
                "/chatIAFlet",
                [
                    ft.AppBar(title=ft.Text("Chat IA"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Container(self.chat_box, expand=True, padding=10),
                    ft.Row(
                        controls=[
                            self.message_input,
                            ft.ElevatedButton("Enviar", on_click=self.send_message, bgcolor=ft.colors.RED, color=ft.colors.WHITE),
                            ft.ElevatedButton("Limpar Chat", on_click=self.clear_chat, bgcolor=ft.colors.RED, color=ft.colors.WHITE),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    # Adiciona o botão de voltar na mesma linha
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()

    def send_message(self, e):
        texto = self.message_input.value.strip()
        if texto.lower() == "sair":
            self.page.go("/")  # Volta para a página principal
            return

        if not texto:
            return

        if getattr(self, 'processing_message', False):  # Verifica se já está processando uma mensagem
            return

        self.processing_message = True  # Define que está processando uma mensagem

        try:
            # Adiciona a mensagem do usuário
            self.chat_box.controls.append(
                ft.Row(
                    [
                        ft.Text(f"Você: {texto}", size=16, color=ft.colors.BLUE_800),
                    ],
                    alignment=ft.MainAxisAlignment.END  # Alinha a mensagem à direita
                )
            )

            # Envia a mensagem e recebe a resposta
            response = self.chat.send_message(texto)

            # Verifica se a resposta é válida
            if hasattr(response, 'text'):
                resposta_texto = response.text  # Ajuste conforme necessário
            else:
                resposta_texto = "Desculpe, não consegui entender."

            # Exibe a resposta na interface
            self.chat_box.controls.append(
                ft.Row(
                    [
                        ft.Text(f"Baymax: {resposta_texto}", size=16, color=ft.colors.RED),
                    ],
                    alignment=ft.MainAxisAlignment.START  # Alinha a resposta à esquerda
                )
            )

            # Limpa o campo de entrada
            self.message_input.value = ""

            # Atualiza a página para mostrar as mensagens
            self.page.update()

            # Faz o Baymax "falar" a resposta
            self.speak(resposta_texto)  # Chamando diretamente, sem thread

            # Rolagem para a última mensagem
            self.chat_box.scroll_to(self.chat_box.controls[-1])
        except Exception as e:
            # Adiciona um erro à caixa de chat se algo falhar
            self.chat_box.controls.append(
                ft.Row(
                    [
                        ft.Text(f"Erro: {str(e)}", size=16, color=ft.colors.RED),
                    ],
                    alignment=ft.MainAxisAlignment.START
                )
            )
            self.page.update()
        finally:
            self.processing_message = False  # Libera a flag de processamento

    def speak(self, text):
        """Transforma texto em fala."""
        try:
            # Cria uma nova instância do TTS a cada chamada
            tts_engine = pyttsx3.init()
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print(f"Erro ao falar: {str(e)}")  # Registra qualquer erro no TTS

    def clear_chat(self, e):
        """Limpa o histórico de chat."""
        self.chat_box.controls.clear()  # Limpa os controles de chat
        self.page.update()  # Atualiza a página

    def build_about_view(self):
        """Constrói a página Sobre Nós."""
        self.page.views.append(
            ft.View(
                "/sobre",
                [
                    ft.AppBar(title=ft.Text("Sobre Nós"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("Este é o Assistente Baymax, criado para ajudar você!", size=24),
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()

    def build_contact_view(self):
        """Constrói a página de Contato."""
        self.page.views.append(
            ft.View(
                "/contato",
                [
                    ft.AppBar(title=ft.Text("Contato"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("Entre em contato conosco pelo e-mail: contato@exemplo.com", size=24),
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()

    def build_error_view(self):
        """Constrói uma página de erro."""
        self.page.views.append(
            ft.View(
                "/error",
                [
                    ft.AppBar(title=ft.Text("Erro"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text("Página não encontrada.", size=24),
                    self.build_back_button(),
                ],
            )
        )
        self.page.update()

    def build_back_button(self):
        """Constrói um botão de voltar."""
        return ft.ElevatedButton("Voltar", on_click=self.go_back)

    def go_back(self, e):
        """Volta para a página anterior."""
        self.page.go("/")  # Volta para a página inicial


if __name__ == "__main__":
    ft.app(target=Inicial)
