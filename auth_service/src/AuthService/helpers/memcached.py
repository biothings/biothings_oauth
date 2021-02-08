import os

import bmemcached


def get_memcached_client():
    """
    Returns a memcached client to be used.

    :return:
        client(pymemcache.client.base.Client): Memecached client.
    """

    memcached_hostname = os.environ.get("MEMCACHED_HOSTNAME")
    memcached_port = os.environ.get("MEMCACHED_PORT_NUMBER")
    memcached_username = os.environ.get("MEMCACHED_USERNAME")
    memcached_password = os.environ.get("MEMCACHED_PASSWORD")
    client = bmemcached.Client(
        [f'{memcached_hostname}:{memcached_port}'],
        memcached_username,
        memcached_password
    )

    return client
