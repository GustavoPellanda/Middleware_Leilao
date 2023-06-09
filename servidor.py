import Pyro5.api
import time
import threading
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import base64

@Pyro5.api.behavior(instance_mode="single")
class Servidor_Leilao(object):
    def __init__(self):
        self.clientes = {}
        self.produtos = []
        self.lances = {}
        self.chave_publica = RSA.import_key(open('public_key.der').read())
    
    @Pyro5.api.expose
    def registrar_cliente(self, nome_cliente, referenciaCliente):
        self.clientes[referenciaCliente] = nome_cliente
        print(f"Novo cliente registrado: {nome_cliente}")

    @Pyro5.api.expose
    def notificar_todos(self, mensagem):
        for referenciaCliente in self.clientes:
            cliente = Pyro5.api.Proxy(referenciaCliente)
            cliente.notificar(mensagem)

    @Pyro5.api.expose
    def registrar_produto(self, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente):
        # Calcula o tempo limite do leilão
        tempo_final_segundos = tempo_final * 1 #3600
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
        
        self.notificar_todos(f"Novo produto '{nome}' foi registrado.\n")
        print(f"Produto '{nome}' registrado por '{nome_cliente}' com prazo final de {tempo_final} horas e preço inicial de R${preco_inicial:.2f}") 

    # Retorna todos os produtos registrados:
    @Pyro5.api.expose
    def obter_produtos(self):
        if not self.produtos:
            return "Nenhum produto cadastrado"
        
        return self.produtos
    
    @Pyro5.api.expose
    def fazer_lance(self, codigo, lance, nome_cliente, signature):
        # Verifica a assinatura
        mensagem = f"{nome_cliente}-{codigo}-{lance}"
        hash_mensagem = SHA256.new(mensagem.encode())  # Reconstrói a mensagem

        try:
            assinatura_bytes = base64.b64decode(signature['data'])  # Decodifica o valor da assinatura de base64
            pkcs1_15.new(self.chave_publica).verify(hash_mensagem, assinatura_bytes)
        except (ValueError, TypeError):
            print(f"A assinatura do lance de {nome_cliente} não é válida.")
            return False
        
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
        self.notificar_todos(f"Novo lance feito no produto {codigo}.\n")
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
                    nome = produto['nome']
                    self.lances.pop(codigo, None)
                    self.produtos.remove(produto)
                    print(f"Lances do produto {codigo} expirados.")
                    self.notificar_todos(f"O leilão do produto {nome} acabou.\n")
                else:
                    print(f"Tempo restante para o produto {produto['codigo']}: {tempo_restante:.2f} segundos")
            time.sleep(10) #Tempo entre as verificações
                    
def main():
    servidor = Servidor_Leilao()
    
    # Registra a aplicação do servidor no serviço de nomes:
    daemon = Pyro5.server.Daemon()
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
