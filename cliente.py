import Pyro5.api
import hashlib
import hmac

@Pyro5.api.expose
class Cliente_Leilao:
    def __init__(cliente, nome, chave):
        cliente.nome = nome
        cliente.chave = chave
        cliente.ref_servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")

    def enviar_mensagem(cliente, mensagem):
        assinatura = hmac.new(cliente.chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()
        cliente.ref_servidor.verificar_assinatura(cliente.nome, mensagem, assinatura)

    def cadastrar_produto(cliente):
        codigo = input("Código do produto: ")
        nome = input("Nome do produto: ")
        descricao = input("Descrição do produto: ")
        preco_inicial = input("Preço inicial: ")
        tempo_final = int(input("Tempo final (em segundos): "))

        mensagem = str(codigo) + nome + descricao + str(preco_inicial) + str(tempo_final)
        assinatura = hmac.new(cliente.chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()

        cliente.ref_servidor.registrar_produto(codigo, nome, descricao, preco_inicial, tempo_final, cliente.nome, assinatura)

        print("Produto cadastrado com sucesso!")

    def menu(cliente):
        while True:
            print("Selecione uma opção:")
            print("1 - Cadastrar Produto")
            print("2 - Consultar Leilões")
            opcao = input("Opção: ")
            if opcao == "1":
                cliente.cadastrar_produto()
            elif opcao == "2":
                cliente.consultar_leiloes()
            else:
                print("Opção inválida. Tente novamente.")
    
    def consultar_leiloes(cliente):
        print("Consultando leilões...")

def main():
    # Registra Cliente_Leilao no Servidor_Leilao
    servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")
    chave = servidor.registrar_cliente("Cliente01")
    # Envia a chave recebida do servidor para o objeto de Cliente_Leilao
    cliente = Cliente_Leilao("Cliente01", chave)

    cliente.menu()

if __name__ == '__main__':
    main()
