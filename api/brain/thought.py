from api.brain.link import Link
from api.brain.model import Model, Component


class Thought(Model):
    def __init__(self, title=None, description=None):
        """
        Initializes new instance of the Thought class.
        :type description: str
        :type title: str
        :param title: Title of the thought
        :param description: Short description of the thought
        """
        super().__init__(components=[
            DefinitionComponent(title, description),
            LinksComponent(self)
        ])

    @property
    def title(self):
        """Gets title of thought."""
        return self.definition.title

    @title.setter
    def title(self, value):
        """Sets title of thought."""
        self.definition.title = value

    @property
    def description(self):
        """Gets short description of thought."""
        return self.definition.description

    @description.setter
    def description(self, value):
        """Sets description of thought."""
        self.definition.description = value

    @property
    def definition(self):
        """
        Returns definition component
        :rtype: DefinitionComponent
        :return: Definition component
        """
        return self.get_component(DefinitionComponent.COMPONENT_NAME)

    @property
    def links(self):
        """
        Returns links component
        :rtype: LinksComponent
        :return: Links component
        """
        return self.get_component(LinksComponent.COMPONENT_NAME)

    def __repr__(self):
        """Returns string representation of thought."""
        return "<Thought:" + str(self.key) + "/" + str(self.title) + ">"


class DefinitionComponent(Component):
    COMPONENT_NAME = "definition"

    def __init__(self, title=None, description=None):
        """
        Initializes new instance of the DefinitionComponent class
        :type title: str
        :type description: str
        :param title: Title
        :param description: Description
        """
        super().__init__(self.COMPONENT_NAME)
        self.__title = title
        self.__description = description

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = value

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    def serialize(self, options=None):
        return {"title": self.title,
                "description": self.description}

    def deserialize(self, data, options=None):
        self.title = data.get("title", None)
        self.description = data.get("description", None)


class LinksComponent(Component):
    """
    Provides interface to link thoughts
    """
    COMPONENT_NAME = "links"
    __correct_kinds = ["child", "parent", "reference"]

    def __init__(self, source=None):
        """
        Initializes new instance of the LinksComponent class
        :type source: Thought
        :param source: Source
        """
        super().__init__(self.COMPONENT_NAME)
        self.__links = {}
        self.__source = source

    def add(self, destination, kind):
        """
        Adds link to destination thought
        :type destination: Thought
        :type kind: str
        :param destination: Destination
        :param kind: Kind of link: [child, parent, reference]
        :raises Exception: If link to specified thought already been added
        :raises ValueError: If kind is incorrect
        :rtype: Link
        :return: Link
        """
        if destination in self.__links:
            raise Exception("Link to specified thought already exist")
        if kind not in self.__correct_kinds:
            raise ValueError("Link kind is not correct: " + kind)
        if self.__source is destination:
            raise ValueError("Unable link thought to itself")
        link = Link(self.__source, destination, kind)
        self.__links[destination] = link
        return link

    def remove(self, destination):
        """
        Removes link to specified thought
        :type destination: Thought
        :param destination: Thought
        :raises Exception: If link to specified thought doesn't exist
        """
        if destination not in self.__links:
            raise Exception("Link to specified thought does not exist")
        del self.__links[destination]

    @property
    def all(self):
        return self.__links

    @property
    def count(self):
        """Returns count of links"""
        return len(self.__links)

    @property
    def children(self):
        """Returns children"""
        return self.__get_links_of_kind("child")

    @property
    def parents(self):
        """Returns parents"""
        return self.__get_links_of_kind("parent")

    @property
    def references(self):
        """Returns references"""
        return self.__get_links_of_kind("reference")

    def by_kind(self, kind):
        """Returns links by specified kind"""
        return self.__get_links_of_kind(kind)

    def on_added(self, composite):
        self.__source = composite

    def serialize(self, options=None):
        result = []
        for key in self.__links:
            l = self.__links[key]
            result.append({"key": l.destination.key, "kind": l.kind})
        if len(result) == 0:
            return None
        return result

    def deserialize(self, data, options=None):
        links_count = len(data)

        # increase depth level to avoid deserialization of
        # whole database
        my_options = (options or {}).copy()
        if "depth" not in my_options:
            my_options["depth"] = 0
        else:
            my_options["depth"] += 1

        # get storage to retrieve linked thoughts
        storage = my_options.get("storage", None)
        if not storage and links_count > 0:
            raise Exception("No 'storage' specified to load linked thoughts")

        # deserialize each link
        for link in data:
            thought = storage.get(link["key"], my_options)
            if thought is None:
                raise Exception("No link '{}' found".format(link["key"]))
            self.add(thought, link["kind"])

    def __get_links_of_kind(self, kind):
        links = filter(lambda x: x.kind == kind, self.__links.values())
        thoughts = map(lambda x: x.destination, links)
        return list(thoughts)
