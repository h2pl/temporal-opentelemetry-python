import json
import logging
from opentelemetry.sdk.resources import Resource

# Import exporters
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

# Trace imports
from opentelemetry.trace import set_tracer_provider, get_tracer_provider
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Metric imports
from opentelemetry import metrics as metrics
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.metrics import MeterProvider, Counter, UpDownCounter, Histogram, ObservableCounter, ObservableUpDownCounter
from opentelemetry.metrics import set_meter_provider, get_meter_provider

# Logs import
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider

# ===== GENERAL SETUP =====

DT_API_URL = "https://aki10000.live.dynatrace.com/api/v2/otlp"
DT_API_TOKEN = "dt0c01.BZCWAQJ6RQ6BYCNCIRD7WIKV.BCAYABR367UJDE3TJ6H7GB7QYGITGLVFQUCD4STGL6QJVDE4BVWOVYCMSMPDO4YI"


merged = dict()
for name in ["dt_metadata_e617c525669e072eebe3d0f08212e8f2.json", "/var/lib/dynatrace/enrichment/dt_metadata.json", "/var/lib/dynatrace/enrichment/dt_host_metadata.json"]:
  try:
    data = ''
    with open(name) as f:
      data = json.load(f if name.startswith("/var") else open(f.read()))
      merged.update(data)
  except:
    pass

merged.update({
  "service.name": "python-quickstart", #TODO Replace with the name of your application
  "service.version": "1.0.1", #TODO Replace with the version of your application
})
resource = Resource.create(merged)


# ===== TRACING SETUP =====

tracer_provider = TracerProvider(sampler=sampling.ALWAYS_ON, resource=resource)
set_tracer_provider(tracer_provider)

tracer_provider.add_span_processor(
  BatchSpanProcessor(
    OTLPSpanExporter(
      endpoint = DT_API_URL + "/v1/traces",
      headers = {
        "Authorization": "Api-Token " + DT_API_TOKEN
      }
    )
  )
)


# ===== METRIC SETUP =====

exporter = OTLPMetricExporter(
  endpoint = DT_API_URL + "/v1/metrics",
  headers = {"Authorization": "Api-Token " + DT_API_TOKEN},
  preferred_temporality = {
    Counter: AggregationTemporality.DELTA,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
    Histogram: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
  }
)

reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader], resource=resource)
set_meter_provider(provider)


# ===== LOG SETUP =====

logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)

logger_provider.add_log_record_processor(
  BatchLogRecordProcessor(OTLPLogExporter(
    endpoint = DT_API_URL + "/v1/logs",
	headers = {"Authorization": "Api-Token " + DT_API_TOKEN}
  ))
)
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Attach OTLP handler to root logger
logging.getLogger().addHandler(handler)

tracer = get_tracer_provider().get_tracer("my-tracer")

with tracer.start_as_current_span("Call to /myendpoint") as span:

    span.set_attribute("http.method", "GET")
    span.set_attribute("net.protocol.version", "1.1")

    #TODO your code goes here

if __name__ == '__main__':
    print(tracer)
    print("ok")