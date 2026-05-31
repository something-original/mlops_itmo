from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    'requests_total',
    'Total number of document comparison requests',
    ['model_name']
)

REQUEST_LATENCY = Histogram(
    'request_duration_seconds',
    'Time spent processing document comparison requests',
    ['model_name']
)

MODEL_ACCURACY = Gauge(
    'accuracy',
    'Accuracy of document comparison',
    ['model_name']
)

MODEL_INFERENCE_TIME = Gauge(
    'inference_time_seconds',
    'Time taken for model inference',
    ['model_name']
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total number of cache hits'
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total number of cache misses'
)

HEALTH_CHECK = Gauge(
    'health',
    'Health status of the document comparison service'
)
