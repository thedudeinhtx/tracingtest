# flask_example.py
import flask
import requests

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

resource = Resource(attributes={SERVICE_NAME: "tracingapp"})

#exporter = ZipkinExporter(endpoint = "http://jaeger-all-in-one-inmemory-agent.tracing.svc:5775/api/v2/spans")
exporter = JaegerExporter(agent_host_name="jaeger-all-in-one-inmemory-agent.tracing.svc", agent_port=6831,)

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(exporter)
trace.set_tracer_provider(provider)
provider.add_span_processor(processor)

app = flask.Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

tracer = trace.get_tracer(__name__)


@app.route("/")
def hello():
    with tracer.start_as_current_span("example-request"):
        requests.get("http://www.example.com")
    return "hello"


app.run(host='0.0.0.0', port=5000)
