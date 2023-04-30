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

    def registrar_produto(servidor, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente, assinatura):
        chave = servidor.clientes[nome_cliente]
        tempo_final_segundos = tempo_final * 3600  # Converter horas em segundos
        mensagem = str(codigo) + nome + descricao + str(preco_inicial) + str(tempo_final)
        assinatura_calculada = hmac.new(chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()

        if assinatura != assinatura_calculada:
            raise ValueError("Assinatura inválida!")

        produto = {
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "preco_inicial": preco_inicial,
            "tempo_final": tempo_final_segundos,
            "nome_cliente": nome_cliente
        }
        servidor.produtos.append(produto)
        print(f"Produto '{nome}' registrado com sucesso com prazo final de {tempo_final} horas.")


    # Retorna todos os produtos registrados:
    def obter_produtos(servidor):
        if not servidor.produtos:
            return "Nenhum produto cadastrado"
        
        return servidor.produtos

def main():
    # Registro de uma instância de Servidor_Leilao no Daemon:
    daemon = Pyro5.api.Daemon()
    servidor = Servidor_Leilao()

    # Registro dos métodos no Name Server:
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(servidor)
    ns.register("Servidor_Leilao", uri)

    print("Servidor do leilão registrado. Pronto para uso!")
    daemon.requestLoop()

if __name__ == '__main__':
    main()
