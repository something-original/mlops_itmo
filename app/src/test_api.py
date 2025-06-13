import json
import time
import requests
from pathlib import Path
from typing import Dict, Any


def test_api_endpoint(
    api_url: str,
    test_dir: str,
    output_file: str = "test_results.json"
) -> Dict[str, Any]:
    """Test API endpoint with test dataset and collect metrics"""
    results = []
    test_files = list(Path(test_dir).glob("*.jpg"))

    for i in range(0, len(test_files), 2):
        if i + 1 >= len(test_files):
            break

        doc1_path = test_files[i]
        doc2_path = test_files[i + 1]

        files = {
            'doc1': ('doc1.jpg', open(doc1_path, 'rb')),
            'doc2': ('doc2.jpg', open(doc2_path, 'rb'))
        }

        start_time = time.time()
        response = requests.post(f"{api_url}/compare", files=files)
        end_time = time.time()

        files['doc1'][1].close()
        files['doc2'][1].close()

        if response.status_code == 200:
            result = response.json()
            result['request_time'] = end_time - start_time
            results.append(result)
        else:
            print(f"Error processing {doc1_path} and {doc2_path}: {response.text}")

    metrics = {
        'total_requests': len(results),
        'avg_request_time': sum(r['request_time'] for r in results) / len(results),
        'avg_inference_time': sum(r['metrics']['inference_time'] for r in results) / len(results),
        'avg_accuracy': sum(r['metrics']['accuracy'] for r in results) / len(results)
    }

    with open(output_file, 'w') as f:
        json.dump({
            'individual_results': results,
            'aggregate_metrics': metrics
        }, f, indent=2)

    return metrics


def main():
    api_url = "http://localhost:8080"
    test_dir = "ocr_model_training/test/images"
    output_file = "test_results.json"

    print("Testing API endpoint...")
    metrics = test_api_endpoint(api_url, test_dir, output_file)

    print("\nTest Results:")
    print(f"Total requests: {metrics['total_requests']}")
    print(f"Average request time: {metrics['avg_request_time']:.2f} seconds")
    print(f"Average inference time: {metrics['avg_inference_time']:.2f} seconds")
    print(f"Average accuracy: {metrics['avg_accuracy']:.2%}")


if __name__ == "__main__":
    main()
