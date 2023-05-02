import Pyro5.api
import hashlib
import hmac

@Pyro5.api.expose
class Cliente_Leilao:
    def __init__(cliente, nome, chave):
        cliente.nome = nome
        cliente.chave = chave
        cliente.servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")
        cliente.produtos = [] # Será utilizado para listar os produtos

    def cadastrar_produto(cliente):
        codigo = input("Código do produto: ")
        nome = input("Nome do produto: ")
        descricao = input("Descrição do produto: ")
        preco_inicial = int(input("Preço inicial: "))
        tempo_final = int(input("Tempo final em horas: "))

        mensagem = str(codigo) + nome + descricao + str(preco_inicial) + str(tempo_final)
        assinatura = hmac.new(cliente.chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()

        cliente.servidor.registrar_produto(codigo, nome, descricao, preco_inicial, tempo_final, cliente.nome, assinatura)

        print(f"Produto '{nome}' registrado com prazo final de {tempo_final} horas e preço inicial de R${preco_inicial:.2f}")

    def listar_produtos(cliente):
        cliente.produtos = cliente.servidor.obter_produtos()
        if cliente.produtos == "Nenhum produto cadastrado":
            print(cliente.produtos)
            return
        
        for produto in cliente.produtos:
            print()
            print(f"Código: {produto['codigo']}")
            print(f"Nome: {produto['nome']}")
            print(f"Descrição: {produto['descricao']}")
            print(f"Preço Inicial: {produto['preco_inicial']:.2f}")
            print(f"Preço Atual: R${produto['preco_atual']:.2f}")
            print(f"Tempo Restante: {produto['prazo_final']:.2f}")
            print(f"Prazo Final: {produto['tempo_restante']:.2f} segundos")
            print(f"Nome do Cliente: {produto['nome_cliente']}")

    def enviar_lance(cliente):
        codigo = input("Código do produto: ")
        lance = int(input("Valor do lance: "))

        mensagem = str(codigo) + str(int(lance))
        assinatura = hmac.new(cliente.chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()

        # Verifica se o lance foi aprovado:
        if not cliente.servidor.fazer_lance(codigo, lance, cliente.nome, assinatura):
            print(f"Lance de R${lance:.2f} não supera lance anterior no produto de código {codigo}.")
            return
        print(f"Lance de R${lance:.2f} enviado ao produto de código {codigo}.")
        
    def menu(cliente):
        while True:
            print("\nSelecione uma opção:")
            print("1 - Cadastrar Produto")
            print("2 - Listar Produtos")
            print("3 - Fazer um lance")
            opcao = input("Opção: ")

            if opcao == "1":
                cliente.cadastrar_produto()
            elif opcao == "2":
                cliente.listar_produtos()
            elif opcao == "3":
                cliente.enviar_lance()
            else:
                print("Opção inválida. Tente novamente.")

def main():
    # Registra Cliente_Leilao no Servidor_Leilao
    servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")
    chave = servidor.registrar_cliente("Cliente01")
    # Envia a chave recebida do servidor para o objeto de Cliente_Leilao
    cliente = Cliente_Leilao("Cliente01", chave)
    cliente.menu()

if __name__ == '__main__':
    main()
