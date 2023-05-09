import Pyro5.api
import threading

class Cliente_Leilao:
    def __init__(self, nome):
        self.nome = nome
        self.servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")
        self.produtos = [] # Será utilizado para listar os produtos

    def cadastrar_produto(self):
        codigo = input("Código do produto: ")
        nome = input("Nome do produto: ")
        descricao = input("Descrição do produto: ")
        preco_inicial = int(input("Preço inicial: "))
        tempo_final = int(input("Tempo final em horas: "))

        self.servidor.registrar_produto(codigo, nome, descricao, preco_inicial, tempo_final, self.nome)

        print(f"Produto '{nome}' registrado com prazo final de {tempo_final} horas e preço inicial de R${preco_inicial:.2f}")

    def listar_produtos(self):
        self.produtos = self.servidor.obter_produtos()
        if self.produtos == "Nenhum produto cadastrado":
            print(self.produtos)
            return
        
        for produto in self.produtos:
            print()
            print(f"Código: {produto['codigo']}")
            print(f"Nome: {produto['nome']}")
            print(f"Descrição: {produto['descricao']}")
            print(f"Preço Inicial: R${produto['preco_inicial']:.2f}")
            print(f"Preço Atual: R${produto['preco_atual']:.2f}")
            print(f"Nome do Cliente: {produto['nome_cliente']}")

    def enviar_lance(self):
        codigo = input("Código do produto: ")
        lance = int(input("Valor do lance: "))

        # Verifica se o lance foi aprovado:
        if not self.servidor.fazer_lance(codigo, lance, self.nome):
            print(f"Lance de R${lance:.2f} não supera lance anterior no produto de código {codigo}.")
            return
        print(f"Lance de R${lance:.2f} enviado ao produto de código {codigo}.")
        
    def menu(self):
        while True:
            print("\nSelecione uma opção:")
            print("1 - Cadastrar Produto")
            print("2 - Listar Produtos")
            print("3 - Fazer um lance")
            opcao = input("Opção: ")

            if opcao == "1":
                self.cadastrar_produto()
            elif opcao == "2":
                self.listar_produtos()
            elif opcao == "3":
                self.enviar_lance()
            else:
                print("Opção inválida. Tente novamente.")

class Callback_Cliente:
    @Pyro5.api.expose
    def notificar(self, notificacao):
        print("Notificação Recebida:", notificacao)

def main():
    # Registra Cliente_Leilao no Servidor_Leilao
    servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")
    servidor.registrar_cliente("Cliente01")
    cliente = Cliente_Leilao("Cliente01")
    
    # Criação do Callback
    callback = Callback_Cliente()
    daemon = Pyro5.api.Daemon()
    callback_uri = Pyro5.api.URI(str(daemon.register(callback)))
    servidor.registrar_callback(callback_uri)

    cliente.menu()

if __name__ == '__main__':
    main()
