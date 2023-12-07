import os

from opentelemetry.trace import get_tracer_provider

tracer = get_tracer_provider().get_tracer("my-tracer")

with tracer.start_as_current_span("Call to /myendpoint") as span:

    span.set_attribute("http.method", "GET")
    span.set_attribute("net.protocol.version", "1.1")

if __name__ == '__main__':
    key = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    print(key)
    #TODO your code goes here
