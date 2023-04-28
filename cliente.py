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

    def interface(cliente):
        while True:
            mensagem = input("Enviar mensagem ao servidor: ")
            cliente.enviar_mensagem(mensagem)

def main():
    # Registra Cliente_Leilao no Servidor_Leilao
    servidor = Pyro5.api.Proxy("PYRONAME:Servidor_Leilao")
    chave = servidor.registrar_cliente("Cliente01")
    # Envia a chave recebida do servidor para o objeto de Cliente_Leilao
    cliente = Cliente_Leilao("Cliente01", chave)

    # Mantém Cliente_Leilao ativo
    cliente.interface()

if __name__ == '__main__':
    main()