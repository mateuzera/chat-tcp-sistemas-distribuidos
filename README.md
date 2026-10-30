# APS 01 - Servidor de Chat Multiusuário (Sockets TCP) - Equipe 11

Projeto desenvolvido para a disciplina de Redes de Computadores e Sistemas Distribuidos.

## Integrantes
- Aldus Monteiro
- Igor Soares
- Izadora Taline Gonçalvez Andrade
- Mateus Martins
- Mateus Barbosa

## Sumário

- [Descrição do Projeto](#-descrição-do-projeto)
- [Funcionalidades Solicitadas](#-funcionalidades-solicitadas)
- [Como Executar](#-como-executar)

## Descrição do Projeto
O objetivo deste trabalho é implementar um sistema de chat multiusuário em tempo real utilizando Sockets TCP. O sistema conta com um servidor persistente que gerencia conexões, retransmite mensagens via broadcast e mantém um buffer de histórico para novos clientes.

## Funcionalidades Solicitadas

- Implementar um servidor de chat multiusuário que permite vários clientes se conectando e trocando mensagens em uma única sala de chat.
- O servidor deve manter uma conexão TCP persistente com cada cliente.
- O cliente se conecta e define seu nome usando o comando CONNECT <nome_usuario>.
- O cliente envia mensagens no chat usando SEND <mensagem>.
- O servidor deve retransmitir toda mensagem enviada imediatamente para todos os outros conectados.
- O servidor deve manter um buffer em memória das últimas N mensagens enviadas.
- Quando um novo cliente se conectar, servidor deve enviar o histórico das últimas N mensagens somente para ele.
- O cliente encerra a conexão através do comando DISCONNECT. 

## Como Executar

Para abrir o servidor, abra um terminal e utilize o comando:

```bash
python server.py
```


Para cada cliente, abra um terminal novo e utilize o comando:

```bash
python client.py
```

No cliente, para entrar no chat e escolher o nome do usuário, utilize:

```bash
CONNECT <nome_usuario>
```

Para enviar mensagens, no cliente que já está dentro do chat, utilize:

```bash
SEND <mensagem>
```

Para se desconectar, utilize:

```bash
DISCONNECT
```

