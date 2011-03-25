from pyparsing import *
ParserElement.setDefaultWhitespaceChars(" \t")

class NonexistentTokenException(Exception):
    """
    An exception that occurs when one tries to register handler for a token
    that is not in the grammar.
    """

    def __init__(self, token_name):
        self.__token_name = token_name

    def __str__(self):
        return "Lexer does not export a token named " + self.__token_name


class Lexer(object):
    """A Class holding a representation of Barnex-Patyk grammar."""

    def __init__(self):
        self.__tokens = {}
        self.__build_grammar()

    def __setitem__(self, key, value):
        self.__tokens[key] = value

    def __getitem__(self, key):
        return self.__tokens[key]

    def register_handlers(self, handlers):
        """
        Sets action handlers for tokens.
        dictionary of handlers - maps token names to parsing action functions
        """

        for token_name in handlers.keys():
            if not token_name in self.__tokens:
                raise NonexistentTokenException(token_name)
            self[token_name].setParseAction(handlers[token_name])

    def unregister_handlers(self):
        """Unsets action handlers for all tokens."""

        for token_name in self.__tokens.keys():
            self[token_name].setParseAction()

    def __build_grammar(self):
        name_charset = alphanums + "-_"
        visibility_charset = "+-#~"

        self["number"] = Word(nums) # TODO: a proper number representation
        self["name"] = Word(name_charset)
        self["string"] = quotedString
        self["visibility"] = Word(visibility_charset, exact=1) \
            .setResultsName("visibility")
        self["static"] = Literal("_").setResultsName("static")

        self.__build_header()
        self.__build_attribute()
        self.__build_operation()
        self.__build_property()
        self.__build_definition()

        self["grammar"] = ZeroOrMore(self["definition"]).setResultsName("code")

    def __build_definition(self):
        element = self["operation"] ^ self["attribute"] ^ self["property"] \
            ^ LineEnd()

        self["definition"] = (ZeroOrMore(LineEnd()) + self["header"] + LineEnd()
            + ZeroOrMore(element + LineEnd())).setResultsName("definition")

    def __build_header(self):
        object_name = self["name"].setResultsName("name")
        parent_name = self["name"].setResultsName("parent")
        prototype = Literal("prototype").setResultsName("prototype")

        self["header"] = (Optional(prototype) + parent_name + 
            Optional(object_name)).setResultsName("header")

    def __build_attribute(self):
        type = self["name"].setResultsName("type")
        name = self["name"].setResultsName("name")
        default = (self["number"] ^ self["string"]).setResultsName("default")

        self["attribute"] = (Optional(self["static"]) + self["visibility"]
            + name + Optional(":" + type) + Optional("=" + default)) \
            .setResultsName("attribute")

    def __build_operation(self):
        name = self["name"].setResultsName("name")
        type = self["name"].setResultsName("type")
        parameter = Group(name + Optional(":" + type)) \
            .setResultsName("parameter")

        parameters = (delimitedList(parameter)).setResultsName("parameters")
        return_type = self["name"].setResultsName("return_type")

        self["operation"] = (Optional(self["static"]) + self["visibility"]
            + name + "(" + Optional(parameters) + ")"
            + Optional(":" + return_type)).setResultsName("operation")

    def __build_property(self):
        multiplicity = ((self["number"] ^ "*") + ".." + (self["number"]
            ^ "*")).setResultsName("multiplicity")
        name = self["name"].setResultsName("name")
        value = Group(multiplicity ^ self["name"] ^ self["string"]) \
            .setResultsName("value")
        values = value.setResultsName("values")

        self["property"] = (name + ":" + values).setResultsName("property")