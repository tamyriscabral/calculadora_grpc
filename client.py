import grpc
import sys

# Importa os módulos gerados
import calculator_pb2 as pb
import calculator_pb2_grpc as rpc

# Configurações
SERVER_ADDRESS = 'localhost:15000'
MAX_NUMBERS = 20

def exibir_menu():
    """Exibe o menu de opções e captura a escolha do usuário."""
    print("\n--- Calculadora Distribuída (gRPC) ---")
    print("1. Somar")
    print("2. Subtrair")
    print("3. Multiplicar")
    print("4. Dividir")
    print("5. Sair")
    
    escolha = input("Escolha uma operação (1-5): ").strip()
    return escolha

def obter_dados_operacao(escolha):
    """
    Solicita os números e retorna a requisição formatada para o gRPC.
    """
    op_map = {
        '1': (pb.CalculationRequest.Operation.SUM, "SOMA"),
        '2': (pb.CalculationRequest.Operation.SUBTRACT, "SUBTRAÇÃO"),
        '3': (pb.CalculationRequest.Operation.MULTIPLY, "MULTIPLICAÇÃO"),
        '4': (pb.CalculationRequest.Operation.DIVIDE, "DIVISÃO"),
    }
    
    if escolha not in op_map:
        return None, None
        
    op_enum, op_nome = op_map[escolha]

    # Exemplo de entrada esperada
    print(f"\nOperação: {op_nome}. Números separados por espaço (máx. {MAX_NUMBERS}).")
    if escolha == '2':
        print("Subtração: O 1º número é subtraído pela soma dos restantes.")
    elif escolha == '4':
        print("Divisão: O 1º número é dividido pelos divisores seguintes.")

    numeros_str = input("Digite os números: ").strip()
    
    try:
        # Tenta converter a string de números para float
        numbers = [float(n) for n in numeros_str.split()]
        
        # O limite de 20 números será verificado no servidor, mas é bom avisar antes
        if len(numbers) > MAX_NUMBERS:
            print(f"ATENÇÃO: Você inseriu mais de {MAX_NUMBERS} números. O servidor pode rejeitar a requisição.")

        # Cria a mensagem de requisição do Protobuf
        request = pb.CalculationRequest(
            operation=op_enum,
            numbers=numbers
        )
        return request, op_nome
        
    except ValueError:
        print("ERRO: Entrada inválida. Certifique-se de que todos são números válidos separados por espaço.")
        return None, None

def run():
    # Cria um canal de comunicação inseguro (para fins de teste)
    with grpc.insecure_channel(SERVER_ADDRESS) as channel:
        # Cria o stub (cliente)
        stub = rpc.CalculatorServiceStub(channel)

        while True:
            escolha = exibir_menu()

            if escolha == '5':
                print("Encerrando o cliente gRPC. Até mais!")
                break
            
            if escolha not in ['1', '2', '3', '4']:
                print("Opção inválida. Por favor, escolha um número de 1 a 5.")
                continue

            request, op_nome = obter_dados_operacao(escolha)
            
            if request is None:
                continue
            
            try:
                # Chama o método RPC no servidor
                print(f"Enviando requisição de {op_nome} para o servidor...")
                response = stub.Calculate(request)
                
                print(f"\n--- Resposta do Servidor ---")
                
                # Verifica se a resposta contém uma mensagem de erro
                if response.error_message:
                    print(f"STATUS: FALHA")
                    print(f"MENSAGEM: {response.error_message}")
                else:
                    # Se não houver erro, exibe o resultado
                    print(f"STATUS: SUCESSO")
                    print(f"RESULTADO: {response.result}")
                    
                print("---------------------------\n")

            except grpc.RpcError as e:
                # Lida com erros de conexão ou tempo limite do gRPC
                print(f"ERRO RPC: Não foi possível conectar ao servidor ou a chamada falhou.")
                print(f"Detalhes: {e.details()}")
                # Sai para evitar loops de erro de conexão
                break 

if __name__ == '__main__':
    run()

