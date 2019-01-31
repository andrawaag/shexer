from dbshx.consts import NT
from dbshx.utils.factories.triple_yielders_factory import get_triple_yielder
from dbshx.core.instance_tracker import InstanceTracker
from dbshx.utils.factories.iri_factory import create_IRIs_from_string_list


def get_instance_tracker(instances_file_input=None, graph_file_input=None,
                         graph_list_of_files_input=None,target_classes=None,
                         file_target_classes=None, input_format=NT):
        instance_yielder = None
        if instances_file_input is not None:
            instance_yielder = get_triple_yielder(source_file=instances_file_input,
                                                  input_format=input_format)
        else:
            instance_yielder = get_triple_yielder(source_file=graph_file_input,
                                                  list_of_source_files=graph_list_of_files_input,
                                                  input_format=input_format)
        list_of_str_target_classes = target_classes if target_classes is not None else _read_target_classes_from_file(file_target_classes)

        return InstanceTracker(target_classes=get_list_of_model_classes(list_of_str_target_classes),
                               triples_yielder=instance_yielder)

def get_list_of_model_classes(list_of_str_target_classes):
    return create_IRIs_from_string_list(list_of_str_target_classes)


def _read_target_classes_from_file(file_target_classes):
    result = []
    with open(file_target_classes, "r") as in_stream:
        for a_line in in_stream:
            candidate = a_line.strip()
            if candidate != "":
                result.append(candidate)
    return result