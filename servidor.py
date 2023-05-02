import Pyro5.api
import hashlib
import hmac
import time
import threading

@Pyro5.api.expose
class Servidor_Leilao:
    def __init__(servidor):
        servidor.clientes = {}
        servidor.produtos = []
        servidor.lances = {}

    def registrar_cliente(servidor, nome_cliente):
        chave = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest() # Criação da chave
        servidor.clientes[nome_cliente] = chave

        print(f"Novo cliente registrado: {nome_cliente}")
        return chave

    def registrar_produto(servidor, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente, assinatura):
        chave = servidor.clientes[nome_cliente]
        mensagem = str(codigo) + nome + descricao + str(preco_inicial) + str(tempo_final)
        assinatura_calculada = hmac.new(chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()
        if assinatura != assinatura_calculada:
            raise ValueError("Assinatura inválida!")
        
        # Calcula o tempo limite do leilão
        tempo_final_segundos = tempo_final * 3600
        prazo_final = time.time() + tempo_final_segundos 
        
        produto = {
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "preco_inicial": preco_inicial,
            "preco_atual": preco_inicial, # Será atualizado quando lances forem feitos
            "prazo_final": prazo_final,
            "tempo_restante": prazo_final - time.time(),  # Calcular o tempo restante em segundos
            "nome_cliente": nome_cliente
        }
        servidor.produtos.append(produto)
        
        print(f"Produto '{nome}' registrado por '{nome_cliente}' com prazo final de {tempo_final} horas e preço inicial de R${preco_inicial:.2f}") 

    # Retorna todos os produtos registrados:
    def obter_produtos(servidor):
        if not servidor.produtos:
            return "Nenhum produto cadastrado"
        
        return servidor.produtos
    
    def fazer_lance(servidor, codigo, lance, nome_cliente, assinatura):
        chave = servidor.clientes.get(nome_cliente)
        mensagem = str(codigo) + str(int(lance))
        assinatura_calculada = hmac.new(chave.encode('utf-8'), mensagem.encode('utf-8'), hashlib.sha256).hexdigest()
        if assinatura != assinatura_calculada:
            raise ValueError("Assinatura inválida!")

        # Verifica se o lance é maior que os anteriores:
        if codigo in servidor.lances:
            if lance <= servidor.lances[codigo]["lance"]:
                print(f"Lance de {nome_cliente} não supera lance anterior no produto {codigo}.")
                return False

        # Atualiza o registro de lances:
        lance_registro = {
            "codigo_produto": codigo,
            "lance": lance,
            "nome_cliente": nome_cliente
        }
        servidor.lances[codigo] = lance_registro

        # Atualiza o preço atual do produto:
        for produto in servidor.produtos:
            if produto["codigo"] == codigo:
                produto["preco_atual"] = lance
                break

        print(f"Lance de {nome_cliente} registrado no produto {codigo} com valor R${lance:.2f}")
        return True

    # Calcula o tempo restante dos leilões:
    def esgotar_leiloes(servidor):
        while True:
            agora = time.time()
            for produto in servidor.produtos:
                tempo_restante = produto['prazo_final'] - agora
                if tempo_restante <= 0:
                    # Deleta:
                    codigo = produto['codigo']
                    servidor.lances.pop(codigo, None)
                    servidor.produtos.remove(produto)
                    print(f"Lances do produto {codigo} expirados.")
                else:
                    print(f"Tempo restante para o produto {produto['codigo']}: {tempo_restante:.2f} segundos")
            time.sleep(60) #Tempo entre as verificações
                    
def main():
    # Registro de uma instância de Servidor_Leilao no Daemon:
    daemon = Pyro5.api.Daemon()
    servidor = Servidor_Leilao()

    # Registro dos métodos no Name Server:
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(servidor)
    ns.register("Servidor_Leilao", uri)

    print("Servidor do leilão registrado. Pronto para uso!")
    
    # Iniciando a thread que verifica os prazos dos leilões:
    thread_verificacao = threading.Thread(target=servidor.esgotar_leiloes)
    thread_verificacao.start()
    
    daemon.requestLoop()

if __name__ == '__main__':
    main()
