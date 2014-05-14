import io


def output_node(node, indent=0, output=None):
    if output is None:
        output = io.StringIO()

    start_tabs = "\t" * indent

    output.write("%s<%s" % (start_tabs, node.name))
    if node.attributes:
        output.write(" ")
        output.write(" ".join(
            "{}='{}'".format(key, value) for key, value in node.attributes.items()
        ))
    output.write(">")

    indented_newline = "\n" + start_tabs + "\t"

    for comment in node.comments:
        output.write(indented_newline)
        output.write("<!--%s-->" % comment)

    if node.child_count:
        output.write("\n")
        for child in node.children:
            output_node(child, indent+1, output)
        output.write(start_tabs)

    if node.text:
        if "\n" not in node.text:
            output.write(node.text)
        else:
            for line in (l.strip() for l in node.text.split("\n")):
                if line:
                    output.write(indented_newline + line)
            output.write("\n" + start_tabs)

    output.write("</%s>\n" % node.name)

    return output