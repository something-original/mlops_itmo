import os
import json
import time
import requests
import argparse
from typing import Dict, Any
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_api_endpoint(
    api_url: str,
    doc1_path: str,
    doc2_path: str,
    output_file: str = "test_results.json"
) -> Dict[str, Any]:
    """Test API endpoint with provided document paths"""

    if not os.path.exists(doc1_path) or not os.path.exists(doc2_path):
        logger.error(f"One or both files not found: {doc1_path}, {doc2_path}")
        return {}

    files = {
        'doc1': (doc1_path, open(doc1_path, 'rb')),
        'doc2': (doc2_path, open(doc2_path, 'rb'))
    }

    try:
        start_time = time.time()
        response = requests.post(f"{api_url}/compare", files=files)
        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            result['request_time'] = end_time - start_time

            with open(output_file, 'a', encoding='utf-8-sig') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info("API Response:")
            logger.info(f"Document 1 text: {result['doc1_text']}")
            logger.info(f"Document 2 text: {result['doc2_text']}")
            logger.info("\nMetrics:")
            logger.info(json.dumps(result['metrics'], indent=2))

            return result
        else:
            logger.error(f"API request failed with status code: {response.status_code}")
            logger.error(f"Error message: {response.text}")
            return {}

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {}
    finally:

        files['doc1'][1].close()
        files['doc2'][1].close()


def main():
    parser = argparse.ArgumentParser(description='Test document comparison API')
    parser.add_argument('doc1_path', help='Path to first document')
    parser.add_argument('doc2_path', help='Path to second document')
    parser.add_argument('--api-url', default='http://localhost:8080', help='API URL')
    parser.add_argument('--output', default='test_results.json', help='Output file for results')

    args = parser.parse_args()

    logger.info("Testing API with documents:")
    logger.info(f"Document 1: {args.doc1_path}")
    logger.info(f"Document 2: {args.doc2_path}")

    test_api_endpoint(args.api_url, args.doc1_path, args.doc2_path, args.output)


if __name__ == "__main__":
    main()
