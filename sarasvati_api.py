import sys

from api.brain.model import IdentityComponent
from api.brain.thought import DefinitionComponent, LinksComponent, Thought
from api.commands import CommandException
from api.instance import set_api
from api.event import Event
from api.plugins import ApplicationPlugin, StoragePlugin, PluginManager, CommandsPlugin, SectionPlugin, ToolboxPlugin
from sarasvati.commands_generic import CreateCommand, LinkCommand


class SarasvatiApi:
    def __init__(self):
        set_api(self)
        self.__events = SarasvatiApiEvents()
        self.__actions = SarasvatiApiActions(self)
        self.__plugins = PluginManager(
            categories={
                "application": ApplicationPlugin,
                "storage": StoragePlugin,
                "commands": CommandsPlugin,
                "section": SectionPlugin,
                "toolbox": ToolboxPlugin
            })
        self.__serialization = SarasvatiApiSerialization()

    @property
    def plugins(self):
        return self.__plugins

    @property
    def events(self):
        return self.__events

    @property
    def actions(self):
        return self.__actions

    @property
    def serialization(self):
        return self.__serialization

    @staticmethod
    def get_one(lst):
        """Returns one element from list, otherwise raises exception"""
        lst_len = len(lst)
        if lst_len == 0:
            raise CommandException("Nothing found")
        elif lst_len > 1:
            raise CommandException("More than one entity found")
        else:
            return lst[0]

    def get_application_plugin(self):
        plugin_name = sys.argv[1] if len(sys.argv) > 1 else "Application.Gui"
        plugins = self.__plugins.find("application")
        filtered = filter(lambda x: x.info.name == plugin_name, plugins)
        result = list(filtered)
        return result[0] if len(result) > 0 else None


class SarasvatiApiEvents:
    def __init__(self):
        self.thoughtCreated = Event()
        self.thoughtSelected = Event()
        self.thoughtChanging = Event()
        self.thoughtChanged = Event()


class SarasvatiApiActions:
    def __init__(self, api):
        self.__api = api

    def create_thought(self, title):
        command = CreateCommand(title)
        thought = self.__api.brain.commands.execute(command)
        self.__api.events.thoughtCreated.notify(thought)
        return thought

    def create_linked_thought(self, root, kind, title):
        ex = self.__api.brain.commands.execute
        thought = ex(CreateCommand(title))
        ex(LinkCommand(root, thought, "child"))
        ex(LinkCommand(thought, root, "parent"))

        self.__api.events.thoughtCreated.notify(thought)
        return thought

    def update_thought(self, thought):
        self.__api.brain.storage.update(thought)
        self.__api.events.thoughtChanged.notify(thought)


class SarasvatiApiSerialization:
    def __init__(self):
        pass

    def get_options(self, storage):
        return {
            "get_component": self.__get_component,
            "get_linked": self.__get_linked(storage)}

    @staticmethod
    # TODO: set serialization map
    def __get_component(key):
        options = {
            IdentityComponent.COMPONENT_NAME: IdentityComponent,
            DefinitionComponent.COMPONENT_NAME: DefinitionComponent,
            LinksComponent.COMPONENT_NAME: LinksComponent}
        res = options.get(key, None)
        if res:
            return res()
        return None

    @staticmethod
    def __get_linked(storage):
        def result(key):
            cached = storage.cache.get(key)
            if not cached:
                thought = Thought("<LAZY>", key=key)
                storage.cache.add(thought, lazy=True)
                return thought
            else:
                return cached
        return result
