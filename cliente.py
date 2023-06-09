import Pyro5.api
import threading
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

class Cliente_Leilao:
    def __init__(self, nome):
        self.nome = nome
        self.servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")
        self.produtos = [] # Será utilizado para listar os produtos
        self.chave_privada = RSA.import_key(open('private_key.der').read())

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

        # Gera a assinatura:
        mensagem = f"{self.nome}-{codigo}-{lance}"
        h = SHA256.new(mensagem.encode())
        assinatura = pkcs1_15.new(self.chave_privada).sign(h)
        assinatura_bytes = bytes(assinatura)

        # Verifica se o lance foi aprovado:
        if not self.servidor.fazer_lance(codigo, lance, self.nome, assinatura_bytes):
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

@Pyro5.api.expose
@Pyro5.api.callback
class cliente_callback(object):
    def notificar(self, notificacao):
        print("\nNotificação Recebida:", notificacao)

    def loopThread(self, daemon):
        daemon.requestLoop()

def main():
    # Obtém a referência da aplicação do servidor no serviço de nomes:
    ns = Pyro5.api.locate_ns()
    uri = ns.lookup("Servidor_Leilao")
    servidor = Pyro5.api.Proxy(uri)

    # Inicializa o Pyro daemon e registra o objeto Pyro callback nele:
    daemon = Pyro5.server.Daemon()
    callback = cliente_callback()
    referenciaCliente = daemon.register(callback)
    
    # Registra Cliente_Leilao no Servidor_Leilao:
    servidor.registrar_cliente("Cliente01", referenciaCliente)
    cliente = Cliente_Leilao("Cliente01")

    # Inicializa a thread para receber notificações do servidor:
    threading.Thread(target=callback.loopThread, args=(daemon,)).start()

    # Mantém a thread principal em execução:
    while True:
        cliente.menu()

if __name__ == '__main__':
    main()
