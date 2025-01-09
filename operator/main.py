import kopf
from .handlers.create import create_agent

@kopf.on.create('agents.example.com', 'v1', 'agenttypes')
def create_fn(spec, name, namespace, logger, body, **kwargs):
    return create_agent(spec, name, namespace, logger, body, **kwargs)

def main():
    kopf.run(clusterwide=True)

if __name__ == "__main__":
    main()