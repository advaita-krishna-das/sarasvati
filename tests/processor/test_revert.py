
def test_revert(api):
    api.processor.execute("/c new")
    api.processor.execute("/r")

    result = api.brain.search.by_title("new")
    assert len(result) == 0


def test_revert_deleted(api):
    root = api.processor.execute("/c root").value
    child = api.processor.execute("/c child parent:root").value
    api.processor.execute("/d child")
    api.processor.execute("/r")

    assert child in root.links.children
    assert root in child.links.parents


def test_revert_history(api):
    api.processor.execute("/c root")
    api.processor.execute("/c child parent:root")
    history = api.processor.execute("/r h").value
    assert history == api.brain.commands.history


def test_revert_activate(api):
    api.processor.execute("/c root")
    api.processor.execute("/a root")
    api.processor.execute("/r")
    assert api.brain.state.active_thought is None


def test_revert_update(api):
    api.processor.execute("/c root")
    api.processor.execute("/a root")
    api.processor.execute("/u root title:new_t desc:new_d")
    api.processor.execute("/r")
    api.processor.execute("/r")
    assert api.brain.state.active_thought.title == "root"
    assert api.brain.state.active_thought.description is None


def test_revert_link(api):
    parent = api.processor.execute("/c parent").value
    child = api.processor.execute("/c child").value
    api.processor.execute("/l child to:parent as:child")
    api.processor.execute("/r")
    assert len(parent.links.all) == 0
    assert len(child.links.all) == 0
