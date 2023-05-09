import Pyro5.api
import time
import threading

@Pyro5.api.expose
class Servidor_Leilao:
    def __init__(self):
        self.clientes = []
        self.produtos = []
        self.lances = {}
        self.callback_uri = None

    def registrar_callback(self, callback):
            print("Callback recebido do cliente", callback)
            self.callback_uri = callback

    def registrar_cliente(self, nome_cliente):
        self.clientes.append(nome_cliente)
        print(f"Novo cliente registrado: {nome_cliente}")

        if self.callback_uri is not None:
            callback = Pyro5.api.Proxy(self.callback_uri)
            callback.notificar("Cliente registrado.")

    def registrar_produto(self, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente):
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
        self.produtos.append(produto)
        
        print(f"Produto '{nome}' registrado por '{nome_cliente}' com prazo final de {tempo_final} horas e preço inicial de R${preco_inicial:.2f}") 

    # Retorna todos os produtos registrados:
    def obter_produtos(self):
        if not self.produtos:
            return "Nenhum produto cadastrado"
        
        return self.produtos
    
    def fazer_lance(self, codigo, lance, nome_cliente):
        # Verifica se o lance é maior que os anteriores:
        if codigo in self.lances:
            if lance <= self.lances[codigo]["lance"]:
                print(f"Lance de {nome_cliente} não supera lance anterior no produto {codigo}.")
                return False

        # Atualiza o registro de lances:
        lance_registro = {
            "codigo_produto": codigo,
            "lance": lance,
            "nome_cliente": nome_cliente
        }
        self.lances[codigo] = lance_registro

        # Atualiza o preço atual do produto:
        for produto in self.produtos:
            if produto["codigo"] == codigo:
                produto["preco_atual"] = lance
                break

        print(f"Lance de {nome_cliente} registrado no produto {codigo} com valor R${lance:.2f}")
        return True

    # Calcula o tempo restante dos leilões:
    def esgotar_leiloes(self):
        while True:
            agora = time.time()
            for produto in self.produtos:
                tempo_restante = produto['prazo_final'] - agora
                if tempo_restante <= 0:
                    # Deleta:
                    codigo = produto['codigo']
                    self.lances.pop(codigo, None)
                    self.produtos.remove(produto)
                    print(f"Lances do produto {codigo} expirados.")
                else:
                    print(f"Tempo restante para o produto {produto['codigo']}: {tempo_restante:.2f} segundos")
            time.sleep(10) #Tempo entre as verificações
                    
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
