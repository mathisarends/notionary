from notionary.util.logging_mixin import LoggingMixin
from notionary.util.singleton_metaclass import SingletonMetaClass


# TODO: Hiers soll nur gemeinsame logik zum erzeugen von NotionPage und Databases rein (Fuzzy matching etc.) -> Gleichzeitig kann hier dann so eine
# generic entity erstellt werden - was perfekt wäre
class NotionEntityFactory(LoggingMixin, metaclass=SingletonMetaClass):

    def __init__(self):
        super().__init__()
