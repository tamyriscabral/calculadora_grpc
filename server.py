import grpc
import time
from concurrent import futures

# Importa os módulos gerados
import calculator_pb2 as pb
import calculator_pb2_grpc as rpc

# Limite de números definido (em concordância com o requisito)
MAX_NUMBERS = 20

# Classe que implementa o serviço definido no .proto
class CalculatorService(rpc.CalculatorServiceServicer):
    
    def _validate_input(self, numbers):
        """Validação de regras: limite de 20 números."""
        num_count = len(numbers)
        if not (1 <= num_count <= MAX_NUMBERS):
            return pb.CalculationResponse(
                error_message=f"A quantidade de números deve ser entre 1 e {MAX_NUMBERS}. Recebido: {num_count}"
            )
        return None # Indica sucesso na validação

    def Calculate(self, request, context):
        """Implementação do método RPC Calculate."""
        
        numbers = list(request.numbers) # Converte para lista
        
        # 1. Validação Geral
        error_response = self._validate_input(numbers)
        if error_response:
            return error_response
        
        op_name = pb.CalculationRequest.Operation.Name(request.operation)
        print(f"Recebida requisição de {op_name} com números: {numbers}")

        try:
            result = 0.0
            
            # Lógica de cálculo
            if request.operation == pb.CalculationRequest.Operation.SUM:
                result = sum(numbers)
                
            elif request.operation == pb.CalculationRequest.Operation.SUBTRACT:
                # Subtrai o primeiro número pela soma dos restantes
                if not numbers:
                    raise ValueError("Subtração requer pelo menos um número.")
                result = numbers[0] - sum(numbers[1:])
                
            elif request.operation == pb.CalculationRequest.Operation.MULTIPLY:
                result = 1.0
                for num in numbers:
                    result *= num
                    
            elif request.operation == pb.CalculationRequest.Operation.DIVIDE:
                if len(numbers) < 2:
                    raise ValueError("Divisão requer pelo menos dois números (dividendo e divisor).")
                
                # O primeiro é o dividendo, os seguintes são divisores
                result = numbers[0]
                for divisor in numbers[1:]:
                    if divisor == 0:
                        raise ZeroDivisionError("Divisão por zero não permitida.")
                    result /= divisor
            
            else:
                return pb.CalculationResponse(error_message="Operação inválida/não suportada.")
                
            # Retorna a resposta de sucesso
            return pb.CalculationResponse(result=result)

        except (ValueError, ZeroDivisionError) as e:
            # Retorna a resposta de erro específica
            return pb.CalculationResponse(error_message=f"ERRO DE CÁLCULO: {e}")
        except Exception as e:
            # Retorna a resposta de erro genérica
            return pb.CalculationResponse(error_message=f"ERRO INTERNO: {e}")

def serve():
    # Cria um pool de threads para o servidor gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Adiciona a implementação da classe de serviço
    rpc.add_CalculatorServiceServicer_to_server(CalculatorService(), server)
    # Define a porta de escuta
    server.add_insecure_port('[::]:15000') 
    server.start()
    print("Servidor gRPC da Calculadora iniciado na porta 15000.")

    # Mantém o servidor rodando
    try:
        while True:
            time.sleep(86400) # Dorme por um dia
    except KeyboardInterrupt:
        server.stop(0)
        print("Servidor desligado.")

if __name__ == '__main__':
    serve()

