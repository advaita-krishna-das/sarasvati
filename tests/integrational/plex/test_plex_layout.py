from plugins.app.gui.plex import PlexLayoutAction


def test_twice_empty(plex, thoughts):
    plex.activate(thoughts["Brain"])
    actions = plex.activate(thoughts["Brain"]).actions
    equal(actions, [])


def test_twice_full_not_empty(plex, thoughts):
    plex.activate(thoughts["Brain"])
    actions = plex.activate(thoughts["Brain"], True).actions
    equal(actions, [
        PlexLayoutAction(thoughts["Brain"], "move", [0, 0]),
        PlexLayoutAction(thoughts["Recipes"], "move", [-100, 100]),
        PlexLayoutAction(thoughts["Tasks"], "move", [100, 100]),
    ])


def test_root(api, plex):
    root = api.execute("/c root").value
    actions = plex.activate(root).actions
    equal(actions, [
        PlexLayoutAction(root, "add", {"pos": [0, 0]})
    ])


def test_root_and_child(api, plex):
    root = api.execute("/c root").value
    child = api.execute("/c child parent:root").value
    actions = plex.activate(root).actions
    equal(actions, [
        PlexLayoutAction(root, "add", {"pos": [0, 0]}),
        PlexLayoutAction(child, "add", {"pos": [0, 0], "key": root.key}),
        PlexLayoutAction(child, "move", [0, 100])
    ])


def test_root_and_two_children(api, plex):
    root = api.execute("/c root").value
    child1 = api.execute("/c child1 parent:root").value
    child2 = api.execute("/c child2 parent:root").value
    actions = plex.activate(root).actions
    equal(actions, [
        PlexLayoutAction(root, "add", {"pos": [0, 0]}),
        PlexLayoutAction(child1, "add", {"pos": [0, 0], "key": root.key}),
        PlexLayoutAction(child1, "move", [-100, 100]),
        PlexLayoutAction(child2, "add", {"pos": [0, 0], "key": root.key}),
        PlexLayoutAction(child2, "move", [100, 100])
    ])


def test_child_and_root(api, plex):
    root = api.execute("/c root").value
    child = api.execute("/c child parent:root").value
    actions = plex.activate(child).actions
    equal(actions, [
        PlexLayoutAction(child, "add", {"pos": [0, 0]}),
        PlexLayoutAction(root, "add", {"pos": [0, 0], "key": child.key}),
        PlexLayoutAction(root, "move", [0, -100])
    ])


def test_child_and_two_root(api, plex):
    root1 = api.execute("/c root1").value
    root2 = api.execute("/c root2").value
    child = api.execute("/c child").value
    api.execute("/l child to:root1 as:parent")
    api.execute("/l child to:root2 as:parent")

    actions = plex.activate(child).actions
    equal(actions, [
        PlexLayoutAction(child, "add", {"pos": [0, 0]}),
        PlexLayoutAction(root1, "add", {"pos": [0, 0], "key": child.key}),
        PlexLayoutAction(root1, "move", [-100, 100]),
        PlexLayoutAction(root2, "add", {"pos": [0, 0], "key": child.key}),
        PlexLayoutAction(root2, "move", [100, 100])
    ])


def test_root_and_reference(api, plex):
    root = api.execute("/c root").value
    ref = api.execute("/c ref").value
    api.execute("/l ref to:root as:reference")

    actions = plex.activate(root).actions
    equal(actions, [
        PlexLayoutAction(root, "add", {"pos": [0, 0]}),
        PlexLayoutAction(ref, "add", {"pos": [0, 0], "key": root.key}),
        PlexLayoutAction(ref, "move", [-100, 0])
    ])


def test_root_and_two_references(api, plex):
    root = api.execute("/c root").value
    ref1 = api.execute("/c ref1").value
    ref2 = api.execute("/c ref2").value
    api.execute("/l ref1 to:root as:reference")
    api.execute("/l ref2 to:root as:reference")

    actions = plex.activate(root).actions
    equal(actions, [
        PlexLayoutAction(root, "add", {"pos": [0, 0]}),
        PlexLayoutAction(ref1, "add", {"pos": [0, 0], "key": root.key}),
        PlexLayoutAction(ref1, "move", [-100, 0]),
        PlexLayoutAction(ref2, "add", {"pos": [0, 0], "key": root.key}),
        PlexLayoutAction(ref2, "move", [-100, -50])
    ])


def test_change_root_and_child1(api, plex):
    root = api.execute("/c root").value
    child1 = api.execute("/c child1 parent:root").value
    child2 = api.execute("/c child2 parent:child1").value
    plex.activate(root)
    actions = plex.activate(child1).actions

    equal(actions, [
        PlexLayoutAction(root, "move", [0, -100]),
        PlexLayoutAction(child1, "move", [0, 0]),
        PlexLayoutAction(child2, "add", {"pos": [0, 100], "key": child1.key})
    ])


def test_change_child_and_root(api, plex):
    root = api.execute("/c root").value
    child1 = api.execute("/c child1 parent:root").value
    child2 = api.execute("/c child2 parent:root").value
    plex.activate(child1)
    actions = plex.activate(root).actions

    equal(actions, [
        PlexLayoutAction(root, "move", [0, 0]),
        PlexLayoutAction(child1, "move", [-100, 100]),
        PlexLayoutAction(child2, "add", {"pos": [0, -100], "key":root.key}),
        PlexLayoutAction(child2, "move", [100, 100])
    ])


def test_change_root_and_children(api, plex):
    root = api.execute("/c root").value
    child11 = api.execute("/c child11 parent:root").value
    child12 = api.execute("/c child12 parent:root").value
    child21 = api.execute("/c child21 parent:child11").value
    plex.activate(root)
    actions = plex.activate(child11).actions

    equal(actions, [
        PlexLayoutAction(root, "move", [0, -100]),
        PlexLayoutAction(child11, "move", [0, 0]),
        PlexLayoutAction(child21, "add", {"pos": [-100, 100], "key": child11.key}),
        PlexLayoutAction(child21, "move", [0, 100]),
        PlexLayoutAction(child12, "remove"),
        PlexLayoutAction(child12, "move", [0, -100]),
    ])


def test_change_root_and_reference(api, plex):
    root = api.execute("/c root").value
    ref = api.execute("/c ref").value
    api.execute("/l ref to:root as:reference")
    state1 = plex.activate(root)
    actions = plex.activate(ref).actions

    equal(actions, [
        PlexLayoutAction(root, "move", [-100, 0]),
        PlexLayoutAction(ref, "move", [0, 0])
    ])


def test_remove_root_and_child(api, plex):
    root = api.execute("/c root").value
    child1 = api.execute("/c child1 parent:root").value
    child2 = api.execute("/c child2 parent:child1").value
    plex.activate(child1)
    actions = plex.activate(child2).actions

    equal(actions, [
        PlexLayoutAction(child2, "move", [0, 0]),
        PlexLayoutAction(child1, "move", [0, -100]),
        PlexLayoutAction(root, "move", [0, -100]),
        PlexLayoutAction(root, "remove")
    ])


def test_remove_linked(api, plex):
    root = api.execute("/c root").value
    child1 = api.execute("/c child1 parent:root").value
    ref = api.execute("/c ref").value
    api.execute("/l ref to:root as:reference")

    plex.activate(root)
    actions = plex.activate(child1).actions

    equal(actions, [
        PlexLayoutAction(ref, "remove"),
        PlexLayoutAction(ref, "move", [0, -100]),
        PlexLayoutAction(child1, "move", [0, 0]),
        PlexLayoutAction(root, "move", [0, -100])
    ])


def equal(l1, l2):
    ll1 = sorted(l1, key=lambda a: (a.thought.key, a.name, a.data))
    ll2 = sorted(l2, key=lambda a: (a.thought.key, a.name, a.data))
    assert ll1 == ll2
