import os
import json
import time
import requests
import argparse
import random
import yaml
from typing import Dict, Any, List, Tuple
import logging
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:

    config_path = os.path.join(Path(__file__).resolve().parent.parent, "config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_random_test_images(test_dir: str, num_pairs: int) -> List[Tuple[str, str]]:

    if not os.path.exists(test_dir):
        logger.error(f"Test directory not found: {test_dir}")
        return []

    image_files = [f for f in os.listdir(test_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if len(image_files) < 2:
        logger.error(f"Not enough images in test directory: {test_dir}")
        return []

    pairs = []
    for _ in range(num_pairs):
        if len(image_files) >= 2:
            pair = random.sample(image_files, 2)
            pairs.append((
                os.path.join(test_dir, pair[0]),
                os.path.join(test_dir, pair[1])
            ))
    return pairs


def test_api_endpoint(
    api_url: str,
    doc1_path: str,
    doc2_path: str,
    output_file: str = "test_results.json"
) -> Dict[str, Any]:

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
            result['doc1_path'] = doc1_path
            result['doc2_path'] = doc2_path

            with open(output_file, 'a', encoding='utf-8-sig') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                f.write('\n')

            logger.info("API Response:")
            logger.info(f"Document 1: {os.path.basename(doc1_path)}")
            logger.info(f"Document 2: {os.path.basename(doc2_path)}")
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
    parser.add_argument('--doc1-path', help='Path to first document')
    parser.add_argument('--doc2-path', help='Path to second document')
    parser.add_argument('--api-url', default='http://localhost:8080', help='API URL')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--test-dir', help='Directory containing test images for random testing')
    parser.add_argument('--iterations', type=int, help='Number of iterations for random testing')
    parser.add_argument('--mode', choices=['regular', 'random'], help='Testing mode')

    args = parser.parse_args()
    config = load_config()

    output_file = args.output or config['testing']['output_file']
    test_dir = args.test_dir or config['testing']['test_dir']
    iterations = args.iterations or config['testing']['iterations']
    mode = args.mode or config['testing']['mode']

    if os.path.exists(output_file):
        os.remove(output_file)

    if mode == 'random':
        logger.info(f"Running random test mode with {iterations} iterations")
        logger.info(f"Test directory: {test_dir}")

        pairs = get_random_test_images(test_dir, iterations)
        if not pairs:
            return

        for i, (doc1_path, doc2_path) in enumerate(pairs, 1):
            logger.info(f"\nIteration {i}/{iterations}")
            test_api_endpoint(args.api_url, doc1_path, doc2_path, output_file)
            time.sleep(10)
    else:
        if not args.doc1_path or not args.doc2_path:
            logger.error("Both doc1-path and doc2-path are required in regular mode")
            return

        logger.info("Testing API with documents:")
        logger.info(f"Document 1: {args.doc1_path}")
        logger.info(f"Document 2: {args.doc2_path}")

        test_api_endpoint(args.api_url, args.doc1_path, args.doc2_path, output_file)


if __name__ == "__main__":
    main()
