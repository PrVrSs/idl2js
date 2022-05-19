from ..js.built_in.constants import DOM_STRING, USV_STRING
from ..js.built_in.jtypes import PrimitiveType


class DOMString(PrimitiveType, name=DOM_STRING):
    pass


class USVString(PrimitiveType, name=USV_STRING):
    pass
