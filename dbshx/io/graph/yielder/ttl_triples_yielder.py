"""
CAUTION! This yielder is able to parse a huge file without loading the whole graph in memory,
but it is expecting a perfectly well-formed ttl. Syntax errors may cause unpredicted failures.

Also, it is ignoring b-nodes, which does not neccesarily make sense for all the sources.
If you want to include bnodes in your classrank computation, you should use/implement
a different yielder.

"""

from dbshx.utils.log import log_to_error
from dbshx.utils.uri import remove_corners, parse_literal
from dbshx.model.IRI import IRI
from dbshx.model.literal import Literal
from dbshx.model.bnode import BNode
from dbshx.model.property import Property


class TtlTriplesYielder(object):
    def __init__(self, source_file):
        self._source_file = source_file
        self._triples_count = 0
        self._error_triples = 0


    def yield_triples(self):
        self._reset_count()
        with open(self._source_file, "r") as in_stream:
            for a_line in in_stream:
                tokens = self._look_for_tokens(a_line.strip())
                if len(tokens) != 3:
                    print a_line
                    for a_token in tokens:
                        print "WOOOOOOOOO,", a_token
                    print "------"
                    self._error_triples += 1
                    # log_to_error(msg="This line caused error: " + a_line,
                    #              source=self._source_file)
                else:
                    # print "MIRA UNA WENAAA ------------- "
                    # print a_line
                    # for a_token in tokens:
                    #     print "EJ,", a_token
                    yield (self._tune_token(tokens[0]), self._tune_prop(tokens[1]), self._tune_token(tokens[2]))
                    self._triples_count += 1
                    # if self._triples_count % 100000 == 0:
                    #     print "Reading...", self._triples_count

    def _look_for_tokens(self, str_line):
        result = []
        current_first_index = 0
        while current_first_index != len(str_line):
            if str_line[current_first_index] == "<":
                last_index = self._look_for_last_index_of_uri_token(str_line, current_first_index)
                result.append(str_line[current_first_index:last_index+1])
                current_first_index = last_index +1
            elif str_line[current_first_index] == '"':
                last_index = self._look_for_last_index_of_literal_token(str_line, current_first_index)
                print str_line, last_index, current_first_index, "'", str_line[current_first_index:last_index + 1], "'"
                result.append(str_line[current_first_index:last_index + 1])
                current_first_index = last_index + 1
            elif str_line[current_first_index] == '.':

                break
            else:
                current_first_index += 1

        return result

    def _look_for_last_index_of_uri_token(self, target_str, first_index):
        target_substring = target_str[first_index:]
        index_sub = target_substring.find(">")
        return index_sub + (len(target_str) - len(target_substring))

    def _look_for_last_index_of_literal_token(self, target_str, first_index):
        target_substring = target_str[first_index:]

        if "^^" not in target_substring:  # Not typed
            success = False
            index_of_quotes = 1
            while not success:
                index_of_second_quotes = target_substring[index_of_quotes+1:].find('"')
                if target_substring[index_of_second_quotes-1] != "\\":
                    success = True
                index_of_quotes = index_of_second_quotes
                # print "tratratra"
            return index_of_quotes + (len(target_str) - len(target_substring))
        else:  # Typed
            # print "Por aqui eh", \
            #     target_substring[target_substring.find("^^"):].find(" ") - 1 , \
            #     "'" , \
            #     target_str[target_substring[target_substring.find("^^"):].find(" ") - 1 + (len(target_str) - len(target_substring))] ,\
            #     "'", target_substring
            return target_substring[target_substring.find("^^"):].find(" ") - 1 + target_str.find("^^")


    def _tune_token(self, a_token):
        if a_token.startswith("<"):
            return IRI(remove_corners(a_token))
        elif a_token.startswith('"'):
            content, elem_type = parse_literal(a_token)
            return Literal(content=content,
                           elem_type=elem_type)
        else:  # a BNode
            return BNode(identifier=a_token)


    def _tune_prop(self, a_token):
        return Property(remove_corners(a_token))


    @property
    def yielded_triples(self):
        return self._triples_count

    @property
    def error_triples(self):
        return self._error_triples

    def _reset_count(self):
        self._error_triples = 0
        self._triples_count = 0
