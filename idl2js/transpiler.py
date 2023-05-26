import logging
from collections import defaultdict
from typing import Optional

from .environment import Environment
from .idl_processor import process_idl
from .idl_to_intermediate import transform_from_idl_to_intermediate
from .intermediate_to_js import transform_from_intermediate_to_js
from .js.built_in.jtypes import type_class_dict
from .std.builder import STDBuilder
from .std.typed_array import TYPED_ARRAY_MAP
from .targets import BaseTarget
from .utils import project_idl_list


logger = logging.getLogger(__name__)


def define_std_types(environment: Environment, builder: STDBuilder) -> None:
    for key, value in type_class_dict.items():
        environment.add_type(key, value(builder))

    for key, value in TYPED_ARRAY_MAP.items():
        environment.add_type(key, value)


def idl_to_intermediate(idls: tuple[str, ...]):
    return transform_from_idl_to_intermediate({
        definition.name: definition
        for idl in process_idl(idls)
        for definition in idl.definitions
    })


class Transpiler:
    def __init__(self, idls: Optional[tuple[str, ...]] = None):
        self._environment = Environment()
        self._instances = defaultdict(list)

        define_std_types(self._environment, STDBuilder())
        self.define_idl_types(
            [
                *project_idl_list(),
                *(idls or []),
            ]
        )

    def define_idl_types(self, idls: tuple[str, ...]) -> None:
        for name, type_class in idl_to_intermediate(idls).items():
            self._environment.add_type(name, type_class)

    def transpile(self, targets: list[BaseTarget]):
        for target in targets:
            transform_from_intermediate_to_js(self._environment, target)

    @property
    def js_instances(self):
        return self._environment.get_variable()
