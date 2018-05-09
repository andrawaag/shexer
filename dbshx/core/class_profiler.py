_S = 0
_P = 1
_O = 2

_ONE_TO_MANY = "+"


class ClassProfiler(object):

    def __init__(self, triples_yielder, target_classes_dict):
        self._triples_yielder = triples_yielder
        self._target_classes_dict = target_classes_dict
        self._instances_shape_dict = {}
        self._classes_shape_dict = self._build_classes_shape_dict_with_just_classes()


    def _build_classes_shape_dict_with_just_classes(self):
        result = {}
        for a_class_key in self._target_classes_dict:
            result[a_class_key] = {}
        return result

    def profile_classes(self):
        self._build_shape_of_instances()
        self._build_class_profile()
        return self._classes_shape_dict


    def _infer_3tuple_features(self, an_instance):
        result = []
        for a_prop in self._instances_shape_dict[an_instance]:
            for a_type in self._instances_shape_dict[an_instance][a_prop]:
                for a_valid_cardinality in self._infer_valid_cardinalities(self._instances_shape_dict[an_instance][a_prop][a_type]):
                    result.append( (a_prop, a_type, a_valid_cardinality) )
        return result

    def _infer_valid_cardinalities(self, a_cardinality):
        if a_cardinality == 1:
            yield 1
        else:
            yield a_cardinality
            yield _ONE_TO_MANY


    def _build_class_profile(self):
        for an_instance in self._instances_shape_dict:
            feautres_3tuple = self._infer_3tuple_features(an_instance)
            for a_class in self._target_classes_dict:
                if self._is_instance_of_class(an_instance, a_class):
                    self._anotate_instance_features_for_class(a_class, feautres_3tuple)


    def _anotate_instance_features_for_class(self, a_class, features_3tuple):
        for a_feature_3tuple in features_3tuple:
            self._introduce_needed_elements_in_shape_classes_dict(a_class, a_feature_3tuple)
            # 3tuple: 0->str_prop, 1->str_type, 2->cardinality
            self._classes_shape_dict[a_class][a_feature_3tuple[0]][a_feature_3tuple[1]][a_feature_3tuple[2]] = 0

    def _introduce_needed_elements_in_shape_classes_dict(self, a_class, a_feature_3tuple):
        str_prop = a_feature_3tuple[0]
        str_type = a_feature_3tuple[1]
        cardinality = a_feature_3tuple[2]
        if str_prop not in self._classes_shape_dict[a_class]:
            self._classes_shape_dict[a_class][str_prop] = {}
        if str_type not in self._classes_shape_dict[a_class][str_prop]:
            self._classes_shape_dict[a_class][str_prop][str_type] = {}
        if cardinality not in self._classes_shape_dict[a_class][str_prop][str_type]:
            self._classes_shape_dict[a_class][str_prop][str_type][cardinality] = 0



    def _is_instance_of_class(self, an_instance_str, a_class_str):
        if an_instance_str in self._target_classes_dict[a_class_str]:
            return True
        return False


    def _build_shape_of_instances(self):
        for a_triple in self._yield_relevant_triples():
            self._anotate_feature_of_target_instance(a_triple)


    def _anotate_feature_of_target_instance(self, a_triple):
        str_subj = a_triple[_S].iri
        str_prop = a_triple[_P].iri
        type_obj = a_triple[_O].elem_type

        self._introduce_needed_elements_in_shape_instances_dict(str_subj=str_subj,
                                                                str_prop=str_prop,
                                                                type_obj=type_obj)

        self._instances_shape_dict[str_subj][str_prop][type_obj] += 1



    def _introduce_needed_elements_in_shape_instances_dict(self, str_subj, str_prop, type_obj):
        if str_subj not in self._instances_shape_dict:
            self._instances_shape_dict[str_subj] = {}
        if str_prop not in self._instances_shape_dict[str_subj]:
            self._instances_shape_dict[str_subj][str_prop] = {}
        if type_obj not in self._instances_shape_dict[str_subj][str_prop]:
            self._instances_shape_dict[str_subj][str_prop][type_obj] = 0


    def _yield_relevant_triples(self):
        for a_triple in self._triples_yielder.yield_triples():
            if self._is_a_relevant_triple(a_triple):
                yield a_triple

    def _is_a_relevant_triple(self, a_triple):
        """
        The subject of the triple must be an instance of at least one of the target classes.
        If it it it returns True. False in the opposite case

        :param a_triple:
        :return: bool
        """
        return True if self._is_subject_in_target_classes(a_triple) else False

    def _is_subject_in_target_classes(self, a_triple):
        str_subj = a_triple[_S].iri
        for class_key in self._target_classes_dict:
            if str_subj in self._target_classes_dict[class_key]:
                return True
        return False