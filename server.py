import socket
import threading

# Configurações do Servidor
HOST = '127.0.0.1'
PORT = 5000
MAX_HISTORICO = 10  # Limite N de mensagens armazenadas no buffer

# Estruturas compartilhadas em memória
clientes = {}        # Mapeamento {socket: nome_usuario}
historico = []       # Buffer circular/lista com as últimas N mensagens
trava = threading.Lock()  # Exclusão mútua para evitar condições de corrida


def salvar_no_historico(mensagem):
    """Armazena a mensagem no buffer respeitando o limite máximo N."""
    historico.append(mensagem)
    if len(historico) > MAX_HISTORICO:
        historico.pop(0)  # Descarta a mensagem mais antiga quando excede N


def broadcast(mensagem, remetente_conn=None):
    """Retransmite a mensagem para todos os clientes ativos, exceto o remetente."""
    for conn in list(clientes.keys()):
        if conn != remetente_conn:
            try:
                conn.sendall((mensagem + "\n").encode('utf-8'))
            except:
                remover_cliente(conn)


def remover_cliente(conn):
    """Remove o cliente do registro ativo e fecha o socket."""
    if conn in clientes:
        nome = clientes.pop(conn)
        print(f"[DESCONECTADO] {nome} saiu do chat.")
        broadcast(f"[SERVIDOR] {nome} saiu da sala.", conn)
    try:
        conn.close()
    except:
        pass


def gerenciar_cliente(conn, addr):
    """
    Mantém a conexão persistente com o cliente e processa o protocolo
    de comandos orientados por linha (CONNECT, SEND, DISCONNECT).
    """
    print(f"[NOVA CONEXÃO] Conectado com {addr}")
    conectado_no_chat = False
    buffer_recebimento = ""

    try:
        while True:
            dados = conn.recv(1024).decode('utf-8')
            if not dados:
                break  # Conexão encerrada pelo cliente

            buffer_recebimento += dados

            # Processa as mensagens delimitadas pelo caractere \n (stream TCP)
            while "\n" in buffer_recebimento:
                linha, buffer_recebimento = buffer_recebimento.split("\n", 1)
                linha = linha.strip()

                if not linha:
                    continue

                partes = linha.split(" ", 1)
                comando = partes[0].upper()
                argumento = partes[1].strip() if len(partes) > 1 else ""

                # Comando 1: CONNECT <nome_usuario>
                if comando == "CONNECT":
                    if conectado_no_chat:
                        conn.sendall("[ERRO] Você já está conectado.\n".encode('utf-8'))
                        continue

                    if not argumento:
                        conn.sendall("[ERRO] Uso correto: CONNECT <nome_usuario>\n".encode('utf-8'))
                        continue

                    # Lock garante envio atômico do histórico antes de novos broadcasts
                    with trava:
                        clientes[conn] = argumento
                        conectado_no_chat = True
                        conn.sendall(f"[SERVIDOR] Bem-vindo(a), {argumento}!\n".encode('utf-8'))

                        # Envio do histórico das últimas N mensagens exclusivamente para este cliente
                        if historico:
                            conn.sendall(f"--- Histórico das últimas {len(historico)} mensagens ---\n".encode('utf-8'))
                            for msg in historico:
                                conn.sendall((msg + "\n").encode('utf-8'))
                            conn.sendall("--------------------------------------------\n".encode('utf-8'))
                        else:
                            conn.sendall("[SERVIDOR] Nenhuma mensagem anterior no histórico.\n".encode('utf-8'))

                        print(f"[REGISTRADO] {addr} identificou-se como '{argumento}'")
                        broadcast(f"[SERVIDOR] {argumento} entrou na sala.", conn)

                # Comando 2: SEND <mensagem>
                elif comando == "SEND":
                    if not conectado_no_chat:
                        conn.sendall("[ERRO] Use CONNECT <nome_usuario> antes de enviar mensagens.\n".encode('utf-8'))
                        continue

                    if not argumento:
                        conn.sendall("[ERRO] Uso correto: SEND <mensagem>\n".encode('utf-8'))
                        continue

                    with trava:
                        nome_usuario = clientes[conn]
                        msg_formatada = f"[{nome_usuario}]: {argumento}"
                        salvar_no_historico(msg_formatada)
                        print(f"[MENSAGEM] {msg_formatada}")
                        broadcast(msg_formatada, conn)

                # Comando 3: DISCONNECT
                elif comando == "DISCONNECT":
                    conn.sendall("[SERVIDOR] Sessão encerrada. Até logo!\n".encode('utf-8'))
                    return  # Sai do loop e finaliza a thread deste cliente no bloco finally

                else:
                    conn.sendall("[ERRO] Comando inválido. Use CONNECT, SEND ou DISCONNECT.\n".encode('utf-8'))

    except Exception as e:
        print(f"[ERRO] Falha com {addr}: {e}")
    finally:
        with trava:
            remover_cliente(conn)


def iniciar_servidor():
    """Inicializa o socket TCP e aguarda conexões concorrentes."""
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()
    servidor.settimeout(1.0)  # Evita travamento no Windows, permitindo captura do Ctrl+C

    print(f"[INICIADO] Servidor ouvindo em {HOST}:{PORT}")
    print(f"[CONFIG] Buffer configurado para as últimas {MAX_HISTORICO} mensagens.")

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