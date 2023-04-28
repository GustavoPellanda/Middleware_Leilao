import Pyro5.api
import hashlib
import hmac
import secrets

@Pyro5.api.expose
class Servidor_Leilao:
    def __init__(serv):
        serv.dic_clientes = {}

    def registrar_cliente(serv, nome_cliente):
        chave = secrets.token_hex(16)  # gerador de chaves
        serv.dic_clientes[nome_cliente] = chave

        print(f"Novo cliente registrado: {nome_cliente}")
        return chave

    def verificar_assinatura(serv, nome_cliente, mensagem, assinatura):
        chave = serv.dic_clientes.get(nome_cliente)
        if not chave:
            raise ValueError(f"Assinatura do cliente '{nome_cliente}' não encontrada.")
        if assinatura != hmac.new(chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest():
            raise ValueError(f"Assinatura do cliente '{nome_cliente}' é inválida.")
        print(f"Assinatura do cliente '{nome_cliente}' verificada!")

        print(f"Mensagem de '{nome_cliente}' recebida: {mensagem}")

def main():
    # Registro de uma instância de Servidor_Leilao no Daemon
    daemon = Pyro5.api.Daemon()
    uri = daemon.register(Servidor_Leilao())

    # Localiza o servidor de nomes
    ns = Pyro5.api.locate_ns()
    # Registra Servidor_Leilao no servidor de nomes
    ns.register("Servidor_Leilao", uri)

    print("Servidor do leilão registrado. Pronto para uso!")
    daemon.requestLoop()

if __name__ == '__main__':
    main()