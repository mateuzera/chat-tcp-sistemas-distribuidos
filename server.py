import socket
import threading

# Configurações de rede locais (loopback e porta para testes)
HOST = '127.0.0.1'
PORT = 5000


def gerenciar_cliente(conn, addr):
    """
    Thread dedicada para manter a conexão persistente com um cliente específico.
    Evita que o loop de leitura bloqueie o atendimento a outros usuários.
    """
    print(f"[NOVA CONEXÃO] Conectado com {addr}")
    try:
        while True:
            # Leitura síncrona do socket TCP (bloqueante para esta thread)
            dados = conn.recv(1024).decode('utf-8')
            if not dados:
                break  # Cliente encerrou o socket do lado dele

            # Eco temporário para validar a troca de mensagens na camada de transporte
            conn.sendall(f"Eco: {dados}".encode('utf-8'))
    except Exception as e:
        print(f"[ERRO] {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] {addr}")


def iniciar_servidor():
    """
    Inicializa o socket TCP, faz o bind e aguarda conexões concorrentes.
    """
    # Criação do socket TCP (IPv4 + SOCK_STREAM)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Permite reutilizar a porta imediatamente caso o processo seja reiniciado
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()

    # Timeout de 1s para o accept não prender a thread principal no Windows (permite Ctrl+C)
    servidor.settimeout(1.0)
    print(f"[INICIADO] Servidor ouvindo em {HOST}:{PORT}")

    try:
        while True:
            try:
                # Bloqueia até uma nova conexão chegar (ou estourar o timeout de 1s)
                conn, addr = servidor.accept()

                # Dispara thread concorrente para atender o cliente
                thread = threading.Thread(target=gerenciar_cliente, args=(conn, addr), daemon=True)
                thread.start()
            except socket.timeout:
                pass  # Permite que o loop itere e capture o sinal de encerramento
    except KeyboardInterrupt:
        print("\n[ENCERRANDO] Servidor desligado.")
    finally:
        servidor.close()


if __name__ == "__main__":
    iniciar_servidor()