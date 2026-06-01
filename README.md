# SQS Worker — Sistemas Distribuídos

Aplicação distribuída em Python com dois serviços (producer e consumer) que se comunicam via fila AWS SQS, executados em containers Docker.

---

## Estrutura do projeto

```
sqs-projeto/
├── docker-compose.yml
├── .env
├── .gitignore
├── producer/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── producer.py
└── consumer/
    ├── Dockerfile
    ├── requirements.txt
    └── consumer.py
```

---

## Como funciona

O **producer** envia mensagens para uma fila SQS a cada 5 segundos. Cada mensagem simula um pedido com produto, quantidade e preço.

O **consumer** escuta a fila usando long polling. Ao receber uma mensagem, processa os dados e só então a deleta da fila. Se ocorrer falha antes da deleção, a mensagem volta automaticamente à fila para ser reprocessada.

Os dois serviços não se comunicam diretamente — a fila SQS é o único ponto de contato entre eles.

```
Producer  -->  AWS SQS  -->  Consumer
              (fila)         (processa e deleta)
```

---

## Pré-requisitos

- Docker e Docker Compose instalados
- Conta AWS.
- Fila SQS criada no console AWS

---

## Configuração

### 1. Criar a fila SQS

Necessario criação da fila SQS para realização de teste do script

### 2. Obter as credenciais AWS

No Vocareum, com o laboratório iniciado (círculo verde), clique em **AWS Details** e depois em **Show** ao lado de **AWS CLI**. Serão exibidas três credenciais temporárias.

As credenciais do laboratório expiram a cada 4 horas. Quando isso ocorrer, reinicie o lab e repita este passo.

### 3. Preencher o arquivo .env

```env
AWS_ACCESS_KEY_ID=ASIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...
AWS_REGION=us-east-1
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/XXXXXXXX
```

O `AWS_SESSION_TOKEN` é obrigatório no ambiente de laboratório. Sem ele a autenticação é rejeitada pela AWS.

---

## Executar

Para testar o codigo
```bash
    docker compose up --build
```

Para para o processo
```bash
    #Para o compose
    docker compose down
    #Para sobre novamente (deve ter buildado para rodar esse comando)
    docker compose up
```
Rodar em background
```
docker compose up -d
```
Ver logs em tempo real
```
docker compose logs -f
```
Encerrar
```
docker compose down
```

---

## Exemplo de saída esperada

```
sqs-producer | 2026-06-01 01:18:26 [PRODUCER] INFO - Iniciando producer...
sqs-producer | 2026-06-01 01:18:26 [PRODUCER] INFO - Fila: https://sqs.us-east-1.amazonaws.com/...
sqs-producer | 2026-06-01 01:18:31 [PRODUCER] INFO - Mensagem #1 enviada | MessageId: abc-123

sqs-consumer | 2026-06-01 01:18:31 [CONSUMER] INFO - Mensagem recebida | MessageId: abc-123
sqs-consumer | 2026-06-01 01:18:31 [CONSUMER] INFO -   → Processando pedido #1
sqs-consumer | 2026-06-01 01:18:31 [CONSUMER] INFO -   → Produto: Produto-2
sqs-consumer | 2026-06-01 01:18:31 [CONSUMER] INFO -   → Quantidade: 1
sqs-consumer | 2026-06-01 01:18:31 [CONSUMER] INFO -   → Preço unitário: R$ 11.50
sqs-consumer | 2026-06-01 01:18:31 [CONSUMER] INFO -   → Total do pedido: R$ 11.50
sqs-consumer | 2026-06-01 01:18:32 [CONSUMER] INFO - Mensagem deletada da fila com sucesso.
```

---

## Conceitos aplicados

**Desacoplamento via fila** — producer e consumer operam de forma independente. Um pode ser reiniciado sem afetar o outro.

**Assincronismo** — o producer não espera o consumer processar. As mensagens ficam armazenadas na fila até serem consumidas.

**Long polling** — o consumer mantém a conexão com a AWS aberta por até 10 segundos aguardando mensagens, reduzindo chamadas desnecessárias e custo.

**Visibility timeout** — ao receber uma mensagem, ela fica invisível para outros consumidores durante o processamento. A deleção só ocorre após sucesso. Em caso de falha, a mensagem retorna à fila automaticamente.

**Containerização** — cada serviço roda em um container isolado com suas próprias dependências. O ambiente é reproduzível em qualquer máquina com Docker.

---