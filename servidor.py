import Pyro5.api
import hashlib
import hmac
import time

@Pyro5.api.expose
class Servidor_Leilao:
    def __init__(servidor):
        servidor.clientes = {}
        servidor.produtos = []

    def registrar_cliente(servidor, nome_cliente):
        chave = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
        servidor.clientes[nome_cliente] = chave

        print(f"Novo cliente registrado: {nome_cliente}")
        return chave

    def verificar_assinatura(servidor, nome_cliente, mensagem, assinatura):
        chave = servidor.clientes[nome_cliente]
        expected = hmac.new(chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, assinatura):
            raise ValueError("Assinatura inválida!")

    def registrar_produto(self, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente, assinatura):
        chave = self.clientes[nome_cliente]
        mensagem = str(codigo) + nome + descricao + str(preco_inicial) + str(tempo_final)
        assinatura_calculada = hmac.new(chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()

        if assinatura != assinatura_calculada:
            raise ValueError("Assinatura inválida!")

        produto = {
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "preco_inicial": preco_inicial,
            "tempo_final": tempo_final,
            "nome_cliente": nome_cliente
        }
        self.produtos.append(produto)
        print(f"Produto '{nome}' registrado com sucesso!")

    def listar_produtos(self):
        for produto in self.produtos:
            print(f"Código: {produto['codigo']}")
            print(f"Nome: {produto['nome']}")
            print(f"Descrição: {produto['descricao']}")
            print(f"Preço Inicial: {produto['preco_inicial']}")
            print(f"Tempo Final: {produto['tempo_final']}")
            print(f"Nome do Cliente: {produto['nome_cliente']}")
            print()

@Pyro5.api.expose
class Produto:
    def __init__(prod, codigo, nome, descricao, preco_inicial, tempo_final):
        prod.codigo = codigo
        prod.nome = nome
        prod.descricao = descricao
        prod.preco_inicial = preco_inicial
        prod.tempo_final = tempo_final

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
