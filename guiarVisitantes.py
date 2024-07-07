import pyttsx3


class GuiarVisitantes:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.alex')

        self.localizacao_dados = self._carregar_dados_localizacao()

    def _carregar_dados_localizacao(self):
        """
        Carrega os dados de localização do campus em um dicionário.
        """
        return {
            "sala de aula": "As salas de aula estão localizadas no prédio principal, distribuídas em vários andares.",
            "escritório": "O escritório da administração está no segundo andar do prédio B.",
            "biblioteca": "A biblioteca está localizada no edifício C, ao lado do refeitório.",
            "reitoria": "A reitoria está no prédio principal, no quarto andar.",
            "estacionamento": "Infelizmente, o campus não possui estacionamento próprio.",
            "atendimento": "O atendimento é realizado de segunda a sexta-feira, das 8 às 21 horas, e aos sábados, das 8 às 12 horas. Para dúvidas, acesse o Fale com a gente ou envie um e-mail para sbcampo@sp.senac.br.",
            "contato": "Você pode entrar em contato pelo telefone (11) 4336-7900 ou pelo e-mail sbcampo@sp.senac.br.",
            "foyer": "O Foyer, área de convivência e eventos, está localizado no edifício principal.",
            "auditório": "O auditório está situado no edifício principal, próximo ao foyer.",
            "estúdio de rádio e vídeo": "O estúdio de rádio e vídeo está no prédio principal, no terceiro andar.",
            "labsenac": "O LabSenac está localizado no edifício principal, no térreo.",
            "laboratório de moda": "O laboratório de moda está no segundo andar do prédio B.",
            "laboratório de design": "O laboratório de design está no segundo andar do prédio B.",
            "laboratório de informática": "O laboratório de informática está no terceiro andar do prédio principal.",
            "laboratório de hardware": "O laboratório de hardware está no terceiro andar do prédio principal.",
            "laboratório de beleza e visagismo": "O laboratório de beleza e visagismo está no segundo andar do prédio B.",
            "laboratório de manicure e pedicure": "O laboratório de manicure e pedicure está no segundo andar do prédio B.",
            "laboratório de bebidas - sala bar": "O laboratório de bebidas, também conhecido como sala bar, está no térreo do prédio principal.",
            "laboratório de gastronomia e nutrição": "O laboratório de gastronomia e nutrição está no térreo do prédio principal."
        }

    def engine_falar(self, texto):
        """
        Converte o texto em fala usando o motor pyttsx3.
        """
        try:
            texto = str(texto)
            self.engine.say(texto)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Erro ao converter texto em fala: {e}")

    def guiar(self, dados_de_voz):
        """
        Fornece informações de localização com base nos dados de voz fornecidos.
        """
        try:
            for local, descricao in self.localizacao_dados.items():
                if local in dados_de_voz:
                    self.engine_falar(descricao)
                    return
            self.engine_falar("Desculpe, não tenho informações sobre esse local. Por favor, pergunte sobre salas de aula, escritórios, ou outras áreas específicas.")
        except Exception as e:
            self.engine_falar("Ocorreu um erro ao processar a solicitação.")
            print(f"Erro ao guiar visitantes: {e}")
