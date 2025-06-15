from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    'document_comparison_requests_total',
    'Total number of document comparison requests',
    ['model_name']
)

REQUEST_LATENCY = Histogram(
    'document_comparison_request_duration_seconds',
    'Time spent processing document comparison requests',
    ['model_name']
)

MODEL_ACCURACY = Gauge(
    'document_comparison_accuracy',
    'Accuracy of document comparison',
    ['model_name']
)

MODEL_INFERENCE_TIME = Gauge(
    'document_comparison_inference_time_seconds',
    'Time taken for model inference',
    ['model_name']
)

CACHE_HITS = Counter(
    'document_cache_hits_total',
    'Total number of cache hits'
)

CACHE_MISSES = Counter(
    'document_cache_misses_total',
    'Total number of cache misses'
)

HEALTH_CHECK = Gauge(
    'document_comparison_health',
    'Health status of the document comparison service'
)
