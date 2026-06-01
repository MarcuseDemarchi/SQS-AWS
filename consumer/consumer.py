import boto3
import json
import os
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CONSUMER] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def criar_cliente_sqs():
    return boto3.client(
        "sqs",
        region_name=os.environ["AWS_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        aws_session_token=os.environ.get("AWS_SESSION_TOKEN")
    )

def processar_mensagem(payload: dict) -> bool:
    logger.info(f"  → Processando pedido #{payload.get('id')}")
    logger.info(f"  → Produto: {payload['dados']['produto']}")
    logger.info(f"  → Quantidade: {payload['dados']['quantidade']}")
    logger.info(f"  → Preço unitário: R$ {payload['dados']['preco']}")

    total = payload["dados"]["quantidade"] * payload["dados"]["preco"]
    logger.info(f"  → Total do pedido: R$ {total:.2f}")

    time.sleep(0.5)
    return True


def consumir_fila(sqs_client, fila_url: str, max_mensagens: int, tempo_espera: int):
    resposta = sqs_client.receive_message(
        QueueUrl=fila_url,
        MaxNumberOfMessages=max_mensagens,
        WaitTimeSeconds=tempo_espera,
        AttributeNames=["All"],
        MessageAttributeNames=["All"],
    )

    mensagens = resposta.get("Messages", [])
    if not mensagens:
        logger.debug("Nenhuma mensagem disponível. Aguardando...")
        return 0

    processadas = 0
    for msg in mensagens:
        receipt_handle = msg["ReceiptHandle"]
        body = json.loads(msg["Body"])

        logger.info(f"Mensagem recebida | MessageId: {msg['MessageId']}")

        try:
            sucesso = processar_mensagem(body)

            if sucesso:
                sqs_client.delete_message(
                    QueueUrl=fila_url,
                    ReceiptHandle=receipt_handle,
                )
                logger.info(f"Mensagem deletada da fila com sucesso.\n")
                processadas += 1
            else:
                logger.warning("Processamento falhou — mensagem permanece na fila para reprocessamento.")

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            logger.warning("Mensagem não deletada — será reprocessada após o VisibilityTimeout.")

    return processadas


def main():
    fila_url = os.environ["SQS_QUEUE_URL"]
    max_mensagens = int(os.environ.get("MAX_MENSAGENS", "5"))
    tempo_espera = int(os.environ.get("WAIT_TIME_SECONDS", "10"))

    logger.info("Iniciando consumer...")
    logger.info(f"Fila: {fila_url}")
    logger.info(f"Máx. mensagens por lote: {max_mensagens}")
    logger.info(f"Long polling timeout: {tempo_espera}s")

    sqs = criar_cliente_sqs()
    total_processadas = 0

    while True:
        try:
            qtd = consumir_fila(sqs, fila_url, max_mensagens, tempo_espera)
            total_processadas += qtd
            if qtd > 0:
                logger.info(f"Total acumulado processado: {total_processadas} mensagens")
        except Exception as e:
            logger.error(f"Erro no ciclo de consumo: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()