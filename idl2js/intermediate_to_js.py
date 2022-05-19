import random
from types import MethodType

from .intermediate.ftypes import (
    FInterface,
    FOptional,
    FType,
    FArgument,
    FSequence,
    FUnion,
    FDictionary,
    FConst,
)
from .js.statements import (
    create_expression,
    create_object,
    create_identifier,
    create_literal,
    create_array,
    create_dict,
    create_property,
)
from .js.instance import Instance as JSInstance
from .js.built_in.jtypes import PrimitiveType
from .utils import unique_name
from .environment import Environment


class NodeTransformer:
    def __init__(self, environment: Environment, transform_runner=None):
        self.environment = environment

        if transform_runner is not None:
            self.build = MethodType(transform_runner, self)

    def build(self, target):
        raise NotImplementedError


def prepare_function_arguments(environment, arguments):
    return [
        build_type(environment=environment, type_object=argument)
        for argument in arguments
    ]


def f_interface_handler(transformer: NodeTransformer, target: FInterface) -> JSInstance:
    progenitor = target.type

    if target.namespace is not None:
        progenitor = f'{target.namespace}.{progenitor}'

    interface = JSInstance(
        type_=target.type,
        ast=create_object(
            name=unique_name(),
            progenitor=progenitor,
            arguments=[
                create_identifier(argument.name)
                for argument in prepare_function_arguments(
                    environment=transformer.environment,
                    arguments=target.constructor.arguments,
                )
            ],
        ),
    )

    transformer.environment.add_instance(name=target.type, instance=interface)

    return interface


def f_argument_handler(transformer, target: FArgument) -> JSInstance:
    argument = build_type(environment=transformer.environment, type_object=target.value)

    if isinstance(argument, JSInstance):
        return argument

    instance = JSInstance(
        type_=argument.type,
        ast=create_expression(
            name=unique_name(),
            expression=argument,
        )
    )

    transformer.environment.add_instance(name=argument.type, instance=instance)

    return instance


def f_optional_handler(transformer, target: FOptional):
    return build_type(environment=transformer.environment, type_object=target.value)


def f_type_handler(transformer, target: FType):
    return build_type(
        environment=transformer.environment,
        type_object=transformer.environment.get_type(target.value),
    )


def base_type_handler(transformer, target: PrimitiveType):
    return create_literal(target.build())


def f_sequence_handler(transformer, target: FSequence):
    elements = []
    for _ in range(random.randint(1, 2)):
        obj = build_type(environment=transformer.environment, type_object=target.items[0])

        if isinstance(obj, JSInstance):
            obj = create_identifier(obj.name)

        elements.append(obj)

    return create_array(elements=elements)


def f_union_handler(transformer, target: FUnion):
    return build_type(environment=transformer.environment, type_object=random.choice(target.items))


def f_dictionary_handler(transformer, target: FDictionary):
    instance = JSInstance(
        type_='',
        ast=create_dict(
            name=unique_name(),
            properties=[
                create_property(
                    key=item.name,
                    value=build_type(environment=transformer.environment, type_object=item.value),
                )
                for item in target.items
            ]
        )
    )

    transformer.environment.add_instance(name='', instance=instance)

    return instance


def f_const_handler(transformer, target: FConst):
    return create_literal(target.value)


def get_handler(target):
    match target:
        case FInterface():
            return f_interface_handler
        case FArgument():
            return f_argument_handler
        case FOptional():
            return f_optional_handler
        case FType():
            return f_type_handler
        case PrimitiveType():
            return base_type_handler
        case FSequence():
            return f_sequence_handler
        case FUnion():
            return f_union_handler
        case FDictionary():
            return f_dictionary_handler
        case FConst():
            return f_const_handler
        case _:
            raise NotImplementedError(f'Not found transformation handler for {target=}')


def build_type(environment, type_object):
    return NodeTransformer(
        environment=environment,
        transform_runner=get_handler(type_object),
    ).build(type_object)


def transform_from_intermediate_to_js(environment, target):
    return build_type(
        environment=environment,
        type_object=environment.get_type(name=target.kind),
    )
