import re


# FIXME: use with caution, can leak memory
uids = {}
uids_document = None


def describe_node(node):
    global uids
    if node is None:
        return ""
    if not hasattr(node, "tag"):
        return "[%s]" % type(node)
    name = node.tag
    if node.get("id", ""):
        name += "#" + node.get("id")
    if node.get("class", "").strip():
        name += "." + ".".join(node.get("class").split())
    if name[:4] in ["div#", "div."]:
        name = name[3:]
    if name in ["tr", "td", "div", "p"]:
        uid = uids.get(node)
        if uid is None:
            uid = uids[node] = len(uids) + 1
        name += "{%02d}" % uid
    return name



RE_COLLAPSE_WHITESPACES = re.compile(r"\s+", re.U)

