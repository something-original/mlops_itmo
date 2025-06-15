import os
import requests
import time
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PROMETHEUS_PORT = os.getenv('PROMETHEUS_PORT') or 9090

ACCURACY_THRESHOLD = 0.8
INFERENCE_TIME_THRESHOLD = 1.0
TRAINING_TIME_THRESHOLD = 3600


def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram configuration missing")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logger.info("Telegram message sent successfully")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {str(e)}")


def check_metrics():
    try:
        response = requests.get(f'http://localhost:{PROMETHEUS_PORT}/metrics')
        metrics = response.text.split('\n')

        current_metrics = {}
        for line in metrics:
            if line.startswith('model_accuracy') or line.startswith('inference_time_seconds') or line.startswith('training_time_seconds'):
                parts = line.split()
                if len(parts) >= 2:
                    metric_name = parts[0]
                    value = float(parts[1])
                    current_metrics[metric_name] = value

        if 'model_accuracy' in current_metrics:
            accuracy = current_metrics['model_accuracy']
            if accuracy < ACCURACY_THRESHOLD:
                message = f"""
                <b>Low Accuracy Alert</b>\nModel accuracy ({accuracy:.2f})
                is below threshold ({ACCURACY_THRESHOLD})
                """
                send_telegram_message(message)

        if 'inference_time_seconds' in current_metrics:
            inference_time = current_metrics['inference_time_seconds']
            if inference_time > INFERENCE_TIME_THRESHOLD:
                message = f"""
                <b>High Inference Time Alert</b>\nInference time ({inference_time:.2f}s)
                exceeds threshold ({INFERENCE_TIME_THRESHOLD}s)
                """
                send_telegram_message(message)

        if 'training_time_seconds' in current_metrics:
            training_time = current_metrics['training_time_seconds']
            if training_time > TRAINING_TIME_THRESHOLD:
                message = f"""
                <b>Long Training Time Alert</b>\nTraining time ({training_time:.2f}s)
                exceeds threshold ({TRAINING_TIME_THRESHOLD}s)
                """
                send_telegram_message(message)

    except Exception as e:
        logger.error(f"Error checking metrics: {str(e)}")


def main():

    logger.info("Starting notification service...")

    while True:
        check_metrics()
        time.sleep(10)


if __name__ == "__main__":
    main()
