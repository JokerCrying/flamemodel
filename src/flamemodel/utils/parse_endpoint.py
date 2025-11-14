from redis.connection import parse_url
from ..d_type import Endpoint, RedisConnectKwargs
from ..exceptions import UnknownEndpointTypeError


def parse_endpoint(endpoint: Endpoint):
    is_cluster = False
    if isinstance(endpoint, str):
        # url mode
        url_kwargs = parse_url(endpoint)
    elif isinstance(endpoint, dict):
        # connect args
        url_kwargs = endpoint
    elif isinstance(endpoint, list):
        # cluster mode
        url_kwargs = {
            'startup_nodes': endpoint
        }
        is_cluster = True
    else:
        err_msg = ('unknown endpoint type, it can be '
                   'string type represents redis url or '
                   'dict type represents redis connect kwargs or'
                   'list type represents redis cluster mode.')
        raise UnknownEndpointTypeError(err_msg, endpoint=endpoint)
    return url_kwargs, is_cluster
