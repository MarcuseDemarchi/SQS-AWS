import boto3
import json
import os
import time
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PRODUCER] %(levelname)s - %(message)s",
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

def enviar_mensagem(sqs_client, fila_url: str, payload: dict) -> str:
    kwargs = {
        "QueueUrl": fila_url,
        "MessageBody": json.dumps(payload),
    }

    resposta = sqs_client.send_message(**kwargs)
    return resposta["MessageId"]


def main():
    fila_url = os.environ["SQS_QUEUE_URL"]
    intervalo = 5

    logger.info("Iniciando producer...")
    logger.info(f"Fila: {fila_url}")
    logger.info(f"Intervalo entre envios: {intervalo}s")

    sqs = criar_cliente_sqs()
    contador = 1

    while True:
        payload = {
            "id": contador,
            "timestamp": datetime.now().isoformat(),
            "mensagem": f"Pedido #{contador} processado pelo sistema de vendas",
            "dados": {
                "produto": f"Produto-{contador % 10 + 1}",
                "quantidade": contador % 5 + 1,
                "preco": round(10.0 + (contador * 1.5) % 100, 2),
            },
        }

        try:
            msg_id = enviar_mensagem(sqs, fila_url, payload)
            logger.info(f"Mensagem #{contador} enviada | MessageId: {msg_id}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem #{contador}: {e}")

        contador += 1
        time.sleep(intervalo)


if __name__ == "__main__":
    main()