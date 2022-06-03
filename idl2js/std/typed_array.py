from ..intermediate.ftypes import FInterface, FFunction

# https://webidl.spec.whatwg.org/#idl-buffer-source-types
# https://developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/TypedArray#Syntax


INT_8_ARRAY = FInterface(
    name='Int8Array',
    attributes={
        'constructor': FFunction(
            name='constructor',
            return_type='self',
            arguments=[],
            is_constructor=True
        )
    }
)


INT_16_ARRAY = FInterface(
    name='Int16Array',
    attributes={
        'constructor': FFunction(
            name='constructor',
            return_type='self',
            arguments=[],
            is_constructor=True
        )
    }
)


ArrayBuffer = FInterface(
    name='ArrayBuffer',
    attributes={
        'constructor': FFunction(
            name='constructor',
            return_type='self',
            arguments=[],
            is_constructor=True
        )
    }
)


TYPED_ARRAY_MAP = {
    'Int8Array':  INT_8_ARRAY,
    'Int16Array': INT_16_ARRAY,
    'ArrayBuffer': ArrayBuffer,
}
