import Pyro5.api
import hashlib
import hmac
import time

@Pyro5.api.expose
class Servidor_Leilao:
    def __init__(servidor):
        servidor.clientes = {}

    def registrar_cliente(servidor, nome_cliente):
        chave = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
        servidor.clientes[nome_cliente] = chave
        return chave

    @Pyro5.api.expose
    def verificar_assinatura(servidor, nome_cliente, mensagem, assinatura):
        chave = servidor.clientes[nome_cliente]
        expected = hmac.new(chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, assinatura):
            raise ValueError("Assinatura inválida!")

    @Pyro5.api.expose
    def registrar_produto(servidor, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente, assinatura):
        mensagem = str(codigo) + nome + descricao + str(preco_inicial) + str(tempo_final)
        servidor.verificar_assinatura(nome_cliente, mensagem, assinatura)
        print("Produto registrado com sucesso!")

@Pyro5.api.expose
class Produto:
    def __init__(prod, codigo, nome, descricao, preco_inicial, tempo_final, servidor):
        prod.codigo = codigo
        prod.nome = nome
        prod.descricao = descricao
        prod.preco_inicial = preco_inicial
        prod.tempo_final = tempo_final
        prod.servidor = servidor

    @Pyro5.api.expose
    def registrar_produto(servidor, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente, assinatura):
        mensagem = str(codigo) + nome + descricao + str(preco_inicial) + str(tempo_final)
        chave_cliente = servidor.clientes_registrados.get(nome_cliente)
        if chave_cliente is None:
            raise ValueError("Cliente não registrado!")
        assinatura_valida = hmac.compare_digest(assinatura, hmac.new(chave_cliente.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest())
        if not assinatura_valida:
            raise ValueError("Assinatura inválida!")
        
        produto = Produto(codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente)
        servidor.produtos.append(produto)

def main():
    # Registro de uma instância de Servidor_Leilao no Daemon:
    daemon = Pyro5.api.Daemon()
    servidor = Servidor_Leilao()

    # Registro dos métodos no Name Server:
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(servidor)
    ns.register("Servidor_Leilao", uri)
    prod_uri = daemon.register(Produto)
    ns.register("Produto", prod_uri)

    print("Servidor do leilão registrado. Pronto para uso!")
    daemon.requestLoop()

if __name__ == '__main__':
    main()
