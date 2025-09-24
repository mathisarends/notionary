from notionary.http.proxy.http_client_caching_interceptor import HttpClientCachingInterceptor, NotionHttpClientProxy


class NotionClientFactory:
    _proxy_instance: NotionHttpClientProxy | None = None

    @classmethod
    def get_cached_proxy(cls) -> NotionHttpClientProxy:
        if cls._proxy_instance is None:
            cls._proxy_instance = NotionHttpClientProxy()
            cls._proxy_instance.add_interceptor(HttpClientCachingInterceptor())
        return cls._proxy_instance
