from decouple import config


class ServiceRegistryClient:
    @property
    def SERVICE_API(self):
        return config("SERVICE_API")

    @property
    def SERVICE_DB(self):
        return config("SERVICE_DB")

    @property
    def SERVICE_WEBAPP(self):
        return config("SERVICE_WEBAPP")

    @property
    def SERVICE_VALHALLA_ENGINE(self):
        return config("SERVICE_VALHALLA_ENGINE")

    @property
    def SERVICE_ROUTING_WRAPPER(self):
        return config("SERVICE_ROUTING_WRAPPER")

    @property
    def SERVICE_VROOM_ENGINE(self):
        return config("SERVICE_VROOM_ENGINE")

    @property
    def SERVICE_CLICKHOUSE(self):
        return config("SERVICE_CLICKHOUSE")

    @property
    def SERVICE_SERVICE_TIME_PREDICTOR(self):
        return config("SERVICE_SERVICE_TIME_PREDICTOR")

    @property
    def SERVICE_RABBITMQ(self):
        return config("SERVICE_RABBITMQ")


service_registry_client = ServiceRegistryClient()
