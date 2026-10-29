import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

def gerenciar_cliente(conn, addr):
    print(f"[NOVA CONEXÃO] Conectado com {addr}")
    try:
        while True:
            dados = conn.recv(1024).decode('utf-8')
            if not dados:
                break
            # eco temporario para testes
            conn.sendall(f"Eco: {dados}".encode('utf-8'))
    except Exception as e:
        print(f"[ERRO] {addr}: {e}")
    finally:
        conn.close()
        print(f"[DESCONECTADO] {addr}")

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()
    servidor.settimeout(1.0)
    print(f"[INICIADO] Servidor ouvindo em {HOST}:{PORT}")

    try:
        while True:
            try:
                conn, addr = servidor.accept()
                thread = threading.Thread(target=gerenciar_cliente, args=(conn, addr), daemon=True)
                thread.start()
            except socket.timeout:
                pass
    except KeyboardInterrupt:
        print("\n[ENCERRANDO] Servidor desligado.")
    finally:
        servidor.close()

if __name__ == "__main__":
    iniciar_servidor()