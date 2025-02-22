import pathlib
import sys

import pytest
import grpc

import handlers.hello_pb2_grpc as hello_services  # noqa: E402, E501

USERVER_CONFIG_HOOKS = ['prepare_service_config']
pytest_plugins = [
    'pytest_userver.plugins.mongo',
    'pytest_userver.plugins.grpc',
]


MONGO_COLLECTIONS = {
    'hello_users': {
        'settings': {
            'collection': 'hello_users',
            'connection': 'admin',
            'database': 'admin',
        },
        'indexes': [],
    },
}


@pytest.fixture(scope='session')
def mongodb_settings():
    return MONGO_COLLECTIONS


@pytest.fixture
def grpc_service(grpc_channel, service_client):
    return hello_services.HelloServiceStub(grpc_channel)


@pytest.fixture(scope='session')
def mock_grpc_hello_session(grpc_mockserver, create_grpc_mock):
    mock = create_grpc_mock(hello_services.HelloServiceServicer)
    hello_services.add_HelloServiceServicer_to_server(
        mock.servicer, grpc_mockserver,
    )
    return mock


@pytest.fixture
def mock_grpc_server(mock_grpc_hello_session):
    with mock_grpc_hello_session.mock() as mock:
        yield mock


@pytest.fixture(scope='session')
def prepare_service_config(grpc_mockserver_endpoint):
    def patch_config(config, config_vars):
        components = config['components_manager']['components']
        components['hello-client']['endpoint'] = grpc_mockserver_endpoint

    return patch_config
