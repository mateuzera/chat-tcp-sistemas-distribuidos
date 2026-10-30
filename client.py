import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 5000


def receber_mensagens(sock):
    """Thread dedicada para escuta assíncrona de broadcast e histórico."""
    while True:
        try:
            dados = sock.recv(1024).decode('utf-8')
            if not dados:
                print("\n[CONEXÃO ENCERRADA PELO SERVIDOR]")
                break
            print(dados, end="")
        except:
            break


def iniciar_cliente():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PORT))
    except Exception as e:
        print(f"Não foi possível conectar ao servidor em {HOST}:{PORT}. Erro: {e}")
        return

    print("=== Conectado ao Servidor TCP ===")
    print("Comandos disponíveis:")
    print("  CONNECT <nome_usuario>  -> Entra no chat e recebe o histórico")
    print("  SEND <mensagem>         -> Envia uma mensagem para a sala")
    print("  DISCONNECT              -> Encerra a sessão e sai\n")

    thread_recebimento = threading.Thread(target=receber_mensagens, args=(cliente,), daemon=True)
    thread_recebimento.start()

    try:
        while True:
            comando = input()
            if not comando.strip():
                continue

            cliente.sendall((comando.strip() + "\n").encode('utf-8'))

            if comando.strip().upper() == "DISCONNECT":
                break
    except KeyboardInterrupt:
        cliente.sendall("DISCONNECT\n".encode('utf-8'))
    finally:
        cliente.close()
        sys.exit(0)


if __name__ == "__main__":
    iniciar_cliente()