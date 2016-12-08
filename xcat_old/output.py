from xml.sax.saxutils import XMLGenerator, escape
import contextlib
import abc
import sys


class Output(abc.ABC):
    def __init__(self, fd=sys.stdout):
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
    def __init__(self, fd=None, include_start=True):
        super().__init__()
        self.include_start=include_start
        self.writer = XMLGeneratorWithComments(self.output, "utf-8")

    def output_started(self):
        if self.include_start:
            self.writer.startDocument()
        self.flush()

    def output_start_node(self, node):
        self.writer.startElement(node.name, node.attributes)

        for comment in node.comments:
            self.writer.writeComment(comment)

        if node.text:
            self.writer.characters(node.text)
        self.flush()

    def output_end_node(self, node):
        self.writer.endElement(node.name)
        self.flush()

    def output_finished(self):
        self.writer.endDocument()
        self.flush()