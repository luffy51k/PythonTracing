import logging
import requests
from base64 import b64encode
from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource as OTLResource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from config import OTLP_ENDPOINT, OTLP_ENDPOINT_USER, OTLP_ENDPOINT_PASSWORD

app = Flask(__name__)

auth_info = f"{OTLP_ENDPOINT_USER}:{OTLP_ENDPOINT_PASSWORD}"
message_bytes = auth_info.encode("ascii")
userAndPass = b64encode(message_bytes).decode("ascii")
headers = {'Authorization': 'Basic %s' % userAndPass}
otlp_exporter = OTLPSpanExporter(endpoint=f"{OTLP_ENDPOINT}",
                                 headers=headers)

# Implement OTLP Tracing
resource = OTLResource(attributes={"service.name": "flask-tracing-demo"})
tracer = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer)

span_processor = BatchSpanProcessor(otlp_exporter)
tracer.add_span_processor(span_processor)

LoggingInstrumentor().instrument(set_logging_format=True)

# Initialize `Instrumentor` for the `requests` library
RequestsInstrumentor().instrument()
# Initialize `Instrumentor` for the `flask` web framework
FlaskInstrumentor().instrument_app(app)


tracer_x = trace.get_tracer(__name__)


@app.route("/")
def index():
    with tracer_x.start_as_current_span("example-request"):
        app.logger.info('route index')
    requests.get('https://google.com/')
    return f"""
<html>
  <p>Ping</p>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    # Send buffered spans.
    tracer.shutdown()
