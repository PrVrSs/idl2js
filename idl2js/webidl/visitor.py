from typing import final

from more_itertools.more import first

from .nodes import (
    Argument,
    Attribute,
    Callback,
    CallbackInterface,
    Const,
    Constructor,
    Definitions,
    Dictionary,
    Enum,
    ExtendedAttribute,
    Field,
    IdlType,
    Includes,
    Infinity,
    Interface,
    InterfaceMixin,
    Iterable_,
    Literal,
    LiteralList,
    MapLike,
    Namespace,
    NaN,
    Null,
    Operation,
    SetLike,
    Typedef,
    Value,
)
from .generated import WebIDLParser, WebIDLParserVisitor
from .utils import setup_type


@final
class Visitor(WebIDLParserVisitor):  # pylint: disable=too-many-public-methods
    def __init__(self, tree):
        self._tree = tree

    def run(self):
        return self.visit(self._tree)

    def visitWebIDL(self, ctx: WebIDLParser.WebIDLContext):
        return ctx.definitions().accept(self)

    def visitDefinitions(self, ctx: WebIDLParser.DefinitionsContext):
        return Definitions(
            definitions=[
                definition.accept(self)
                for definition in ctx.extendedDefinition()
            ],
        )

    def visitExtendedDefinition(self, ctx: WebIDLParser.ExtendedDefinitionContext):
        definition = ctx.definition().accept(self)

        if extended_attribute := ctx.extendedAttributeList():
            definition.ext_attrs = extended_attribute.accept(self)

        return definition

    def visitDictionary(self, ctx: WebIDLParser.DictionaryContext):
        return Dictionary(
            partial=ctx.PARTIAL() is not None,
            name=ctx.IDENTIFIER().getText(),
            members=[member.accept(self) for member in ctx.dictionaryMembers()],
            inheritance=ctx.inheritance() and ctx.inheritance().accept(self),
        )

    def visitTypedef(self, ctx: WebIDLParser.TypedefContext):
        setup_type(
            idl_type := ctx.typeWithExtendedAttributes().accept(self),
            'typedef-type',
        )

        return Typedef(idl_type=idl_type, name=ctx.IDENTIFIER().getText())

    def visitIncludesStatement(self, ctx: WebIDLParser.IncludesStatementContext):
        return Includes(
            target=ctx.target.text, includes=ctx.includes.text)  # type: ignore

    def visitEnum_(self, ctx: WebIDLParser.Enum_Context):
        return Enum(
            name=ctx.IDENTIFIER().getText(),
            values=[
                Literal(
                    type='enum-value', value=enum_value.getText().strip('"'))
                for enum_value in ctx.StringLiteral()
            ]
        )

    def visitInterfaceRest(self, ctx: WebIDLParser.InterfaceRestContext):
        return Interface(
            name=ctx.IDENTIFIER().getText(),
            inheritance=ctx.inheritance() and ctx.inheritance().accept(self),
            members=[member.accept(self) for member in ctx.interfaceMembers()],
        )

    def visitPartialInterfaceRest(self, ctx: WebIDLParser.PartialInterfaceRestContext):
        return Interface(
            name=ctx.IDENTIFIER().getText(),
            members=[
                member.accept(self) for member in ctx.partialInterfaceMembers()
            ],
        )

    def visitMixinRest(self, ctx: WebIDLParser.MixinRestContext):
        return InterfaceMixin(
            name=ctx.IDENTIFIER().getText(),
            members=[
                member.accept(self) for member in ctx.mixinMembers()
            ],
        )

    def visitNamespace(self, ctx: WebIDLParser.NamespaceContext):
        return Namespace(
            name=ctx.IDENTIFIER().getText(),
            members=[
                member.accept(self) for member in ctx.namespaceMembers()
            ],
            partial=ctx.PARTIAL() is not None,
        )

    def visitPartial(self, ctx: WebIDLParser.PartialContext):
        interface_or_mixin = ctx.partialInterfaceOrPartialMixin().accept(self)

        interface_or_mixin.partial = True

        return interface_or_mixin

    def _member_with_extended_attribute(self, member, extended_attribute):
        member = member.accept(self)

        if extended_attribute is not None:
            member.ext_attrs = extended_attribute.accept(self)

        return member

    def visitNamespaceMembers(self, ctx: WebIDLParser.NamespaceMembersContext):
        return self._member_with_extended_attribute(
            ctx.namespaceMember(), ctx.extendedAttributeList())

    def visitMixinMembers(self, ctx: WebIDLParser.MixinMembersContext):
        return self._member_with_extended_attribute(
            ctx.mixinMember(), ctx.extendedAttributeList())

    def visitPartialInterfaceMembers(self, ctx: WebIDLParser.PartialInterfaceMembersContext):
        return self._member_with_extended_attribute(
            ctx.partialInterfaceMember(), ctx.extendedAttributeList())

    def visitInterfaceMembers(self, ctx: WebIDLParser.InterfaceMembersContext):
        return self._member_with_extended_attribute(
            ctx.interfaceMember(), ctx.extendedAttributeList())

    def visitDictionaryMembers(self, ctx: WebIDLParser.DictionaryMembersContext):
        return self._member_with_extended_attribute(
            ctx.dictionaryMember(), ctx.extendedAttributeList())

    def visitCallbackInterfaceMembers(self, ctx: WebIDLParser.CallbackInterfaceMembersContext):
        return self._member_with_extended_attribute(
            ctx.callbackInterfaceMember(), ctx.extendedAttributeList())

    def visitMixinMember(self, ctx: WebIDLParser.MixinMemberContext):
        if ctx.READONLY() is None:
            return ctx.getChild(0).accept(self)

        attribute = ctx.attributeRest().accept(self)
        attribute.readonly = True

        return attribute

    def visitDictionaryMember(self, ctx: WebIDLParser.DictionaryMemberContext):
        if type_ := ctx.typeWithExtendedAttributes():
            idl_type = type_.accept(self)
        else:
            idl_type = ctx.type_().accept(self)

        if default := ctx.default_():
            default = default.accept(self)

        setup_type(idl_type, 'dictionary-type')

        return Field(
            required=ctx.REQUIRED() is not None,
            name=ctx.IDENTIFIER().getText(),
            default=default,
            idl_type=idl_type,
        )

    def visitNamespaceMember(self, ctx: WebIDLParser.NamespaceMemberContext):
        if regular_operation := ctx.regularOperation():
            return self._operation(regular_operation)

        attribute = ctx.attributeRest().accept(self)
        attribute.readonly = True

        return attribute

    def visitStringifier(self, ctx: WebIDLParser.StringifierContext):
        if stringifier := ctx.stringifierRest():
            stringifier = stringifier.accept(self)
            stringifier.special = 'stringifier'

            return stringifier

        return Operation(name='', idl_type=None, special='stringifier')

    def visitStringifierRest(self, ctx: WebIDLParser.StringifierRestContext):
        if regular_operation := ctx.regularOperation():
            return self._operation(regular_operation)

        attribute = ctx.attributeRest().accept(self)
        attribute.readonly = ctx.READONLY() is not None

        return attribute

    def visitStaticMember(self, ctx: WebIDLParser.StaticMemberContext):
        member = ctx.staticMemberRest().accept(self)
        member.special = 'static'

        return member

    def visitStaticMemberRest(self, ctx: WebIDLParser.StaticMemberRestContext):
        if regular_operation := ctx.regularOperation():
            return self._operation(regular_operation)

        attribute = ctx.attributeRest().accept(self)
        attribute.readonly = ctx.READONLY() is not None

        return attribute

    def visitCallbackOrInterfaceOrMixin(self, ctx: WebIDLParser.CallbackOrInterfaceOrMixinContext):
        if callback := ctx.callbackRestOrInterface():
            return callback.accept(self)

        return ctx.interfaceOrMixin().accept(self)

    def visitCallbackRestOrInterface(self, ctx: WebIDLParser.CallbackRestOrInterfaceContext):
        if callback_rest := ctx.callbackRest():
            return callback_rest.accept(self)

        return CallbackInterface(
            name=ctx.IDENTIFIER().getText(),
            inheritance=None,
            members=[
                member.accept(self)
                for member in ctx.callbackInterfaceMembers()
            ],
        )

    def visitInterfaceOrMixin(self, ctx: WebIDLParser.InterfaceOrMixinContext):
        if interface_rest := ctx.interfaceRest():
            return interface_rest.accept(self)

        return ctx.mixinRest().accept(self)

    def _operation(self, regular_operation, special=''):
        return_type, (name, arguments) = regular_operation.accept(self)

        setup_type(return_type, 'return-type')

        return Operation(
            name=name,
            arguments=arguments,
            idl_type=return_type,
            special=special,
        )

    def visitMaplikeRest(self, ctx: WebIDLParser.MaplikeRestContext):
        return MapLike(
            idl_type=[
                type_with_extended_attr.accept(self)
                for type_with_extended_attr in ctx.typeWithExtendedAttributes()
            ],
            readonly=ctx.READONLY() is not None,
        )

    def visitSetlikeRest(self, ctx: WebIDLParser.SetlikeRestContext):
        return SetLike(
            idl_type=[ctx.typeWithExtendedAttributes().accept(self)],
            readonly=ctx.READONLY() is not None,
        )

    def visitCallbackInterfaceMember(self, ctx: WebIDLParser.CallbackInterfaceMemberContext):
        if regular_operation := ctx.regularOperation():
            return self._operation(regular_operation)

        return ctx.const_()

    def visitConstValue(self, ctx: WebIDLParser.ConstValueContext):
        if boolean_literal := ctx.booleanLiteral():
            return boolean_literal.accept(self)

        if float_literal := ctx.floatLiteral():
            return float_literal.accept(self)

        return Literal(type='number', value=ctx.IntegerLiteral().getText())

    def visitFloatLiteral(self, ctx: WebIDLParser.FloatLiteralContext):
        if ctx.NAN():
            return NaN()

        if ctx.INFINITY():
            return Infinity(negative=False)

        if ctx.MINUS_INFINITY():
            return Infinity(negative=True)

        return Literal(type='number', value=ctx.DecimalLiteral().getText())

    def visitBooleanLiteral(self, ctx: WebIDLParser.BooleanLiteralContext):
        return Literal(type='boolean', value=ctx.getText() == 'true')

    def visitConst_(self, ctx: WebIDLParser.Const_Context):
        return Const(
            idl_type=ctx.constType().accept(self),
            value=ctx.constValue().accept(self),
            name=ctx.IDENTIFIER().getText(),
        )

    def visitCallbackRest(self, ctx: WebIDLParser.CallbackRestContext):
        if arguments := ctx.argumentList():
            arguments = arguments.accept(self)

        setup_type(idl_type := ctx.returnType().accept(self), 'return-type')

        return Callback(
            name=ctx.IDENTIFIER().getText(),
            idl_type=idl_type,
            arguments=arguments or [],
        )

    def visitConstructor(self, ctx: WebIDLParser.ConstructorContext):
        if arguments := ctx.argumentList():
            arguments = arguments.accept(self)

        return Constructor(arguments=arguments or [])

    def visitAttributeRest(self, ctx: WebIDLParser.AttributeRestContext):
        setup_type(
            idl_type := ctx.typeWithExtendedAttributes().accept(self),
            'attribute-type',
        )

        return Attribute(
            name=ctx.attributeName().accept(self), idl_type=idl_type)

    def visitIterable(self, ctx: WebIDLParser.IterableContext):
        if arg_list := ctx.optionalArgumentList():
            arg_list = arg_list.accept(self)

        return Iterable_(
            arguments=arg_list or [],
            async_=ctx.ASYNC() is not None,
            idl_type=[
                type_with_extended_attr.accept(self)
                for type_with_extended_attr in ctx.typeWithExtendedAttributes()
            ],
        )

    def visitOptionalArgumentList(self, ctx: WebIDLParser.OptionalArgumentListContext):
        if arg_list := ctx.argumentList():
            arg_list = arg_list.accept(self)

        return arg_list or []

    def visitOperation(self, ctx: WebIDLParser.OperationContext):
        return self._operation(
            ctx.regularOperation(), ctx.special and ctx.special.text or '')

    def visitRegularOperation(self, ctx: WebIDLParser.RegularOperationContext):
        return ctx.returnType().accept(self), ctx.operationRest().accept(self)

    def visitOperationRest(self, ctx: WebIDLParser.OperationRestContext):
        if name := ctx.operationName():
            name = name.accept(self)

        if arguments := ctx.argumentList():
            arguments = arguments.accept(self)

        return name or '', arguments or []

    def visitArgumentList(self, ctx: WebIDLParser.ArgumentListContext):
        return [argument.accept(self) for argument in ctx.argument()]

    def visitArgument(self, ctx: WebIDLParser.ArgumentContext):
        argument = ctx.argumentRest().accept(self)

        if ext_attrs := ctx.extendedAttributeList():
            argument.ext_attrs = ext_attrs.accept(self)

        return argument

    def visitExtendedAttributeList(self, ctx: WebIDLParser.ExtendedAttributeListContext):
        return [
            extendedAttribute.accept(self)
            for extendedAttribute in ctx.extendedAttribute()
        ]

    @staticmethod
    def _extended_attribute(name, rhs=None, arguments=None):
        return ExtendedAttribute(name=name, rhs=rhs, arguments=arguments or [])

    def visitExtendedAttributeNoArgs(self, ctx: WebIDLParser.ExtendedAttributeNoArgsContext):
        return self._extended_attribute(ctx.IDENTIFIER().getText())

    def visitExtendedAttributeNamedArgList(
            self, ctx: WebIDLParser.ExtendedAttributeNamedArgListContext):
        return self._extended_attribute(
            name=ctx.name.text,  # type: ignore
            arguments=ctx.argumentList().accept(self),
            rhs=Literal(type='identifier', value=ctx.rhs.text),  # type: ignore
        )

    def visitExtendedAttributeArgList(self, ctx: WebIDLParser.ExtendedAttributeArgListContext):
        return self._extended_attribute(
            name=ctx.name.text,  # type: ignore
            arguments=ctx.argumentList().accept(self),
        )

    def visitExtendedAttributeIdentList(self, ctx: WebIDLParser.ExtendedAttributeIdentListContext):
        return self._extended_attribute(
            name=ctx.name.text,  # type: ignore
            rhs=ctx.identifierList().accept(self)
        )

    def visitExtendedAttributeIdent(self, ctx: WebIDLParser.ExtendedAttributeIdentContext):
        return self._extended_attribute(
            name=ctx.name.text, rhs=ctx.rhs.accept(self))  # type: ignore

    def visitIdentifierList(self, ctx: WebIDLParser.IdentifierListContext):
        identifiers = [
            identifier.accept(self) for identifier in ctx.identifier()
        ]

        return LiteralList(
            value=[Value(value=identifier.value) for identifier in identifiers],
            type=f'{first(identifiers).type}-list',
        )

    def visitArgumentRest(self, ctx: WebIDLParser.ArgumentRestContext):
        if default := ctx.default_():
            default = default.accept(self)

        if optional := ctx.OPTIONAL():
            idl_type = ctx.typeWithExtendedAttributes().accept(self)
        else:
            idl_type = ctx.type_().accept(self)

        setup_type(idl_type, 'argument-type')

        return Argument(
            idl_type=idl_type,
            name=ctx.argumentName().accept(self),
            optional=optional is not None,
            default=default,
            variadic=ctx.ELLIPSIS() is not None,
        )

    def visitReadOnlyMember(self, ctx: WebIDLParser.ReadOnlyMemberContext):
        member = ctx.readOnlyMemberRest().accept(self)
        member.readonly = True

        return member

    def visitInheritAttribute(self, ctx: WebIDLParser.InheritAttributeContext):
        attribute = ctx.attributeRest().accept(self)
        attribute.special = 'inherit'

        return attribute

    def visitTypeWithExtendedAttributes(
            self, ctx: WebIDLParser.TypeWithExtendedAttributesContext):
        idl_type = ctx.type_().accept(self)

        if ext_attrs := ctx.extendedAttributeList():
            idl_type.ext_attrs = ext_attrs.accept(self)

        return idl_type

    def visitDefault_(self, ctx: WebIDLParser.Default_Context):
        return ctx.defaultValue().accept(self)

    def visitDefaultValue(self, ctx: WebIDLParser.DefaultValueContext):
        if str_ := ctx.StringLiteral():
            return Literal(type='string', value=str_.getText().strip('"'))

        if const_value := ctx.constValue():
            return const_value.accept(self)

        if ctx.LEFT_BRACE():
            return Literal(type='dictionary', value={})

        if ctx.NULL():
            return Null()

        return Literal(type='sequence', value=[])

    def visitType_(self, ctx: WebIDLParser.Type_Context):
        if single_type := ctx.singleType():
            return single_type.accept(self)

        return IdlType(
            idl_type=ctx.unionType().accept(self),
            nullable=ctx.null_() is not None,
            union=True,
        )

    def visitUnionType(self, ctx: WebIDLParser.UnionTypeContext):
        return [
            member_type.accept(self) for member_type in ctx.unionMemberType()
        ]

    def visitUnionMemberType(self, ctx: WebIDLParser.UnionMemberTypeContext):
        nullable = ctx.null_() is not None

        if ext_attrs := ctx.extendedAttributeList():
            ext_attrs = ext_attrs.accept(self)

        if distinguishable_type := ctx.distinguishableType():
            return IdlType(
                idl_type=distinguishable_type.accept(self),
                ext_attrs=ext_attrs or [],
                nullable=nullable,
            )

        if generic := ctx.genericType():
            return IdlType(
                idl_type=[generic.accept(self)],
                ext_attrs=ext_attrs or [],
                nullable=nullable
            )

        return IdlType(
            idl_type=ctx.unionType().accept(self),
            nullable=nullable,
            union=True,
        )

    def visitReturnType(self, ctx: WebIDLParser.ReturnTypeContext):
        if void := ctx.VOID():
            return IdlType(idl_type=void.getText())

        return ctx.type_().accept(self)

    def visitUnsignedIntegerType(
            self, ctx: WebIDLParser.UnsignedIntegerTypeContext):
        integer_type = ctx.integerType().accept(self)

        if ctx.UNSIGNED():
            integer_type = f'unsigned {integer_type}'

        return integer_type

    def visitSingleType(self, ctx: WebIDLParser.SingleTypeContext):
        nullable = ctx.null_() is not None

        if any_ := ctx.ANY():
            return IdlType(idl_type=any_.getText())

        if promise := ctx.promiseType():
            return IdlType(idl_type=[promise.accept(self)], generic='Promise')

        if generic := ctx.genericType():
            return IdlType(
                idl_type=[generic.accept(self)],
                generic='sequence',
                nullable=nullable,
            )

        distinguishable_type = ctx.distinguishableType().accept(self)

        if isinstance(distinguishable_type, IdlType):
            return distinguishable_type

        return IdlType(
            idl_type=distinguishable_type, nullable=nullable)

    def visitGenericType(self, ctx: WebIDLParser.GenericTypeContext):
        return ctx.typeWithExtendedAttributes().accept(self)

    def visitDistinguishableType(
            self, ctx: WebIDLParser.DistinguishableTypeContext):
        if type_ := ctx.primitiveType():
            return type_.accept(self)

        if type_ := ctx.stringType():
            return type_.accept(self)

        if type_ := ctx.bufferRelatedType():
            return type_.accept(self)

        if type_ := ctx.recordType():
            return type_.accept(self)

        return ctx.getChild(0).getText()

    def visitRecordType(self, ctx: WebIDLParser.RecordTypeContext):
        return IdlType(
            generic='record',
            idl_type=[
                IdlType(idl_type=ctx.stringType().accept(self)),
                ctx.typeWithExtendedAttributes().accept(self),
            ]
        )

    def visitConstType(self, ctx: WebIDLParser.ConstTypeContext):
        if idl_type := ctx.primitiveType():
            idl_type = idl_type.accept(self)

        return IdlType(
            type='const-type', idl_type=idl_type or ctx.IDENTIFIER().getText())

    def visitPrimitiveType(self, ctx: WebIDLParser.PrimitiveTypeContext):
        if type_ := ctx.unsignedIntegerType():
            return type_.accept(self)

        if type_ := ctx.unrestrictedFloatType():
            return type_.accept(self)

        return ctx.getChild(0).getText()

    def visitUnrestrictedFloatType(self, ctx: WebIDLParser.UnrestrictedFloatTypeContext):
        float_type = ctx.floatType().accept(self)

        if ctx.UNRESTRICTED():
            float_type = f'unrestricted {float_type}'

        return float_type

    def visitPromiseType(self, ctx: WebIDLParser.PromiseTypeContext):
        return ctx.returnType().accept(self)

    def visitIntegerType(self, ctx: WebIDLParser.IntegerTypeContext):
        if long := ' '.join(long.getText() for long in ctx.LONG()):
            return long

        return ctx.getText()

    def visitFloatType(self, ctx: WebIDLParser.FloatTypeContext):
        return ctx.getText()

    def visitStringType(self, ctx: WebIDLParser.StringTypeContext):
        return ctx.getText()

    def visitOperationName(self, ctx: WebIDLParser.OperationNameContext):
        return ctx.getText()

    def visitArgumentName(self, ctx: WebIDLParser.ArgumentNameContext):
        return ctx.getText()

    def visitAttributeName(self, ctx: WebIDLParser.AttributeNameContext):
        return ctx.getText()

    def visitInheritance(self, ctx: WebIDLParser.InheritanceContext):
        return ctx.IDENTIFIER().getText()

    def visitBufferRelatedType(self, ctx: WebIDLParser.BufferRelatedTypeContext):
        return ctx.getText()

    def visitOther(self, ctx: WebIDLParser.OtherContext):
        if ctx.IntegerLiteral():
            type_ = 'integer'
        elif ctx.DecimalLiteral():
            type_ = 'decimal'
        elif ctx.StringLiteral():
            type_ = 'string'
        else:
            type_ = 'identifier'

        return Literal(type=type_, value=ctx.getText())
