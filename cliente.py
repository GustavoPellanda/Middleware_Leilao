import Pyro5.api
import hashlib
import hmac

@Pyro5.api.expose
class Cliente_Leilao:
    def __init__(cliente, nome, chave):
        cliente.nome = nome
        cliente.chave = chave
        cliente.servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")
        cliente.produtos = []

    def cadastrar_produto(cliente):
        codigo = input("Código do produto: ")
        nome = input("Nome do produto: ")
        descricao = input("Descrição do produto: ")
        preco_inicial = input("Preço inicial: ")
        tempo_final = int(input("Tempo final (em segundos): "))

        mensagem = str(codigo) + nome + descricao + str(preco_inicial) + str(tempo_final)
        assinatura = hmac.new(cliente.chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()

        cliente.servidor.registrar_produto(codigo, nome, descricao, preco_inicial, tempo_final, cliente.nome, assinatura)

        print(f"Produto '{nome}' registrado com sucesso!")

    def listar_produtos(cliente):
        cliente.produtos = cliente.servidor.obter_produtos()
        for produto in cliente.produtos:
            print(f"Código: {produto['codigo']}")
            print(f"Nome: {produto['nome']}")
            print(f"Descrição: {produto['descricao']}")
            print(f"Preço Inicial: {produto['preco_inicial']}")
            print(f"Tempo Final: {produto['tempo_final']}")
            print(f"Nome do Cliente: {produto['nome_cliente']}")
            print()
        
    def menu(cliente):
        while True:
            print("\nSelecione uma opção:")
            print("1 - Cadastrar Produto")
            print("2 - Listar Produtos")
            opcao = input("Opção: ")

            if opcao == "1":
                cliente.cadastrar_produto()
            elif opcao == "2":
                cliente.listar_produtos()
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
