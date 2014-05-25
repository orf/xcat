import xmltodict
import io
from xml.sax.saxutils import XMLGenerator, escape
import contextlib
import json
import abc


class Output(abc.ABC):
    def __init__(self, fd):
        self.output = fd

    @abc.abstractmethod
    def output_start_node(self, node):
        pass

    @abc.abstractmethod
    def output_end_node(self, node):
        pass

    def output_started(self):
        return  # Optional

    def output_finished(self):
        return  # Optional


class XMLGeneratorWithComments(XMLGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = 0

    @contextlib.contextmanager
    def indent(self, extra_tabs=0):
        self._write("\t" * (self.tabs + extra_tabs))
        yield
        self._write("\n")

    def writeComment(self, comment):
        with self.indent():
            self._write("<!--{}-->".format(escape(comment)))

    def characters(self, content):
        with self.indent():
            super().characters(content)

    def startElement(self, name, attrs):
        with self.indent():
            super().startElement(name, attrs)
        self.tabs += 1

    def endElement(self, name):
        self.tabs -= 1
        with self.indent():
            super().endElement(name)


class XMLOutput(Output):
    def __init__(self, fd):
        super().__init__(fd)
        self.writer = XMLGeneratorWithComments(self.output, "utf-8")

    def output_started(self):
        self.writer.startDocument()

    def output_start_node(self, node):
        self.writer.startElement(node.name, node.attributes)

        for comment in node.comments:
            self.writer.writeComment(comment)

        if node.text:
            self.writer.characters(node.text)

    def output_end_node(self, node):
        self.writer.endElement(node.name)

    def output_finished(self):
        self.writer.endDocument()


class JSONOutput(XMLOutput):
    def __init__(self, fd):
        # Hijack the FD
        self.old_fd = fd
        super().__init__(io.StringIO())

    def output_finished(self):
        super().output_finished()
        # self.output will be a StringIO object with some XML inside. Get it's value and convert it to JSON
        self.output.seek(0)
        result = xmltodict.parse(self.output.getvalue())
        self.old_fd.write(bytes(json.dumps(result, indent=4), encoding="utf-8"))
        self.old_fd.flush()