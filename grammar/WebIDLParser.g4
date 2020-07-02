parser grammar WebIDLParser;

options { tokenVocab=WebIDLLexer; }


webIDL
    : definitions? EOF
    ;

definitions
    : extendedDefinition+
    ;

extendedDefinition
    : extendedAttributeList? definition
    ;

definition
    : callbackOrInterfaceOrMixin
    | namespace
    | partial
    | dictionary
    | enum_
    | typedef
    | includesStatement
    ;

callbackOrInterfaceOrMixin
    : CALLBACK callbackRestOrInterface
    | INTERFACE interfaceOrMixin
    ;

interfaceOrMixin
    : interfaceRest
    | mixinRest
    ;

interfaceRest
    : IDENTIFIER inheritance? LEFT_BRACE interfaceMembers* RIGHT_BRACE SEMI
    ;

partial
    : PARTIAL INTERFACE partialInterfaceOrPartialMixin
    ;

partialInterfaceOrPartialMixin
    : partialInterfaceRest
    | mixinRest
    ;

partialInterfaceRest
    : IDENTIFIER LEFT_BRACE partialInterfaceMembers* RIGHT_BRACE SEMI
    ;

interfaceMembers
    : extendedAttributeList? interfaceMember
    ;

interfaceMember
    : partialInterfaceMember
    | constructor
    ;

partialInterfaceMembers
    : extendedAttributeList? partialInterfaceMember
    ;

partialInterfaceMember
    : const_
    | operation
    | stringifier
    | staticMember
    | iterable
    | readOnlyMember
    | readWriteAttribute
    | readWriteMaplike
    | readWriteSetlike
    | inheritAttribute
    ;

inheritance
    : COLON IDENTIFIER
    ;

mixinRest
    : MIXIN IDENTIFIER LEFT_BRACE mixinMembers* RIGHT_BRACE SEMI
    ;

mixinMembers
    : extendedAttributeList? mixinMember
    ;

mixinMember
    : const_
    | regularOperation
    | stringifier
    | READONLY? attributeRest
    ;

includesStatement
    : target=IDENTIFIER INCLUDES includes=IDENTIFIER SEMI
    ;

callbackRestOrInterface
    : callbackRest
    | INTERFACE IDENTIFIER LEFT_BRACE callbackInterfaceMembers* RIGHT_BRACE SEMI
    ;


callbackInterfaceMembers
    : extendedAttributeList? callbackInterfaceMember
    ;

callbackInterfaceMember
    : const_
    | regularOperation
    ;

const_
    : CONST constType IDENTIFIER EQUAL_SYMBOL constValue SEMI
    ;

constValue
    : booleanLiteral
    | floatLiteral
    | IntegerLiteral
    ;

readOnlyMember
    : READONLY readOnlyMemberRest
    ;

readOnlyMemberRest
    : attributeRest
    | maplikeRest
    | setlikeRest
    ;

readWriteAttribute
    : attributeRest
    ;

inheritAttribute
    : INHERIT attributeRest
    ;

attributeRest
    : ATTRIBUTE typeWithExtendedAttributes attributeName SEMI
    ;

attributeName
    : attributeNameKeyword=(ASYNC | REQUIRED)
    | IDENTIFIER
    ;

defaultValue
    : constValue
    | StringLiteral
    | LEFT_BRACKET RIGHT_BRACKET
    | LEFT_BRACE RIGHT_BRACE
    | NULL
    ;

operation
    : special=(GETTER | SETTER | DELETER)? regularOperation
    ;

regularOperation
    : returnType operationRest
    ;

operationRest
    : operationName? LEFT_PAREN argumentList? RIGHT_PAREN SEMI
    ;

operationName
    : operationNameKeyword
    | IDENTIFIER
    ;

operationNameKeyword
    : INCLUDES
    ;

argumentList
    : argument (COMMA argument)*
    ;

argument
    : extendedAttributeList? argumentRest
    ;

argumentRest
    : OPTIONAL typeWithExtendedAttributes argumentName default_?
    | type_ ELLIPSIS? argumentName
    ;

argumentName
    : argumentNameKeyword
    | IDENTIFIER
    ;

constructor
    : CONSTRUCTOR LEFT_PAREN argumentList? RIGHT_PAREN SEMI
    ;

stringifier
    : STRINGIFIER (stringifierRest | SEMI)
    ;

stringifierRest
    : READONLY? attributeRest
    | regularOperation
    ;

staticMember
    : STATIC staticMemberRest
    ;

staticMemberRest
    : READONLY? attributeRest
    | regularOperation
    ;

iterable
    : ITERABLE LEFT_ANGLE typeWithExtendedAttributes (COMMA typeWithExtendedAttributes)? RIGHT_ANGLE SEMI
    | ASYNC ITERABLE LEFT_ANGLE typeWithExtendedAttributes (COMMA typeWithExtendedAttributes)? RIGHT_ANGLE optionalArgumentList? SEMI
    ;

optionalArgumentList
    : LEFT_PAREN argumentList? RIGHT_PAREN
    ;

readWriteMaplike
    : maplikeRest
    ;

maplikeRest
    : READONLY? MAPLIKE LEFT_ANGLE typeWithExtendedAttributes COMMA typeWithExtendedAttributes RIGHT_ANGLE SEMI
    ;

readWriteSetlike
    : setlikeRest
    ;

setlikeRest
    : READONLY? SETLIKE LEFT_ANGLE typeWithExtendedAttributes RIGHT_ANGLE SEMI
    ;

namespace
    : PARTIAL? NAMESPACE IDENTIFIER LEFT_BRACE namespaceMembers* RIGHT_BRACE SEMI
    ;

namespaceMembers
    : extendedAttributeList? namespaceMember
    ;

namespaceMember
    : regularOperation
    | READONLY attributeRest
    ;

dictionary
    : DICTIONARY IDENTIFIER inheritance? LEFT_BRACE dictionaryMembers* RIGHT_BRACE SEMI
    | PARTIAL DICTIONARY IDENTIFIER LEFT_BRACE dictionaryMembers* RIGHT_BRACE SEMI
;

dictionaryMembers
    : extendedAttributeList? dictionaryMember
    ;

dictionaryMember
    : REQUIRED typeWithExtendedAttributes IDENTIFIER SEMI
    | type_ IDENTIFIER default_? SEMI
    ;

default_
    : EQUAL_SYMBOL defaultValue
    ;

enum_
    : ENUM IDENTIFIER LEFT_BRACE StringLiteral (COMMA StringLiteral?)* RIGHT_BRACE SEMI
    ;

callbackRest
    : IDENTIFIER EQUAL_SYMBOL returnType LEFT_PAREN argumentList? RIGHT_PAREN SEMI
    ;

typedef
    : TYPEDEF typeWithExtendedAttributes IDENTIFIER SEMI
    ;

type_
    : singleType
    | unionType null_?
    ;

typeWithExtendedAttributes
    : extendedAttributeList? type_
    ;

extendedAttributeList
    : LEFT_BRACKET extendedAttribute (COMMA extendedAttribute)* RIGHT_BRACKET
    ;

extendedAttribute
    : name=IDENTIFIER                                                                   #extendedAttributeNoArgs
    | name=IDENTIFIER EQUAL_SYMBOL LEFT_PAREN identifierList RIGHT_PAREN                #extendedAttributeIdentList
    | name=IDENTIFIER EQUAL_SYMBOL rhs=IDENTIFIER  LEFT_PAREN argumentList RIGHT_PAREN  #extendedAttributeNamedArgList
    | name=IDENTIFIER EQUAL_SYMBOL rhs=identifier                                       #extendedAttributeIdent
    | name=IDENTIFIER LEFT_PAREN argumentList RIGHT_PAREN                               #extendedAttributeArgList
    ;

identifierList
    : identifier (COMMA identifier)*
    ;

identifier
    : other
    ;

returnType
    : type_
    | VOID
    ;

singleType
    : distinguishableType null_?
    | genericType null_?
    | promiseType
    | ANY
    ;

unionType
    : LEFT_PAREN unionMemberType (OR unionMemberType)+ RIGHT_PAREN
    ;

unionMemberType
    : extendedAttributeList? distinguishableType null_?
    | extendedAttributeList? genericType null_?
    | unionType null_?
    ;

genericType
    : generic=(SEQUENCE | FROZEN_ARRAY | OBSERVABLE_ARRAY) LEFT_ANGLE typeWithExtendedAttributes RIGHT_ANGLE
    ;

distinguishableType
    : primitiveType
    | stringType
    | bufferRelatedType
    | recordType
    | IDENTIFIER
    | OBJECT
    | SYMBOL
    ;

primitiveType
    : unsignedIntegerType
    | unrestrictedFloatType
    | BOOLEAN
    | BYTE
    | OCTET
    ;

constType
    : primitiveType
    | IDENTIFIER
    ;

promiseType
    : PROMISE LEFT_ANGLE returnType RIGHT_ANGLE
    ;

recordType
    : RECORD LEFT_ANGLE stringType COMMA typeWithExtendedAttributes RIGHT_ANGLE
    ;

unrestrictedFloatType
    : UNRESTRICTED? floatType
    ;

floatType
    : FLOAT
    | DOUBLE
    ;

unsignedIntegerType
    : UNSIGNED? integerType
    ;

integerType
    : SHORT
    | LONG LONG?
    ;

stringType
    : BYTE_STRING
    | DOM_STRING
    | USV_STRING
    ;

bufferRelatedType
    : ARRAY_BUFFER
    | DATA_VIEW
    | INT_8_ARRAY
    | INT_16_ARRAY
    | INT_32_ARRAY
    | UINT_8_ARRAY
    | UINT_16_ARRAY
    | UINT_32_ARRAY
    | UINT_8_CLAMPED_ARRAY
    | FLOAT_32_ARRAY
    | FLOAT_64_ARRAY
    ;

booleanLiteral
    : TRUE
    | FALSE
    ;

floatLiteral
    : DecimalLiteral
    | MINUS_INFINITY
    | INFINITY
    | NAN
    ;

null_
    : QUESTION_SYMBOL
    ;

other
    : IntegerLiteral
    | DecimalLiteral
    | IDENTIFIER
    | StringLiteral
    | OTHER
    | MINUS
    | MINUS_INFINITY
    | DOT
    | ELLIPSIS
    | COLON
    | SEMI
    | LEFT_ANGLE
    | EQUAL_SYMBOL
    | RIGHT_ANGLE
    | QUESTION_SYMBOL
    | BYTE_STRING
    | DOM_STRING
    | FROZEN_ARRAY
    | INFINITY
    | NAN
    | OBSERVABLE_ARRAY
    | PROMISE
    | USV_STRING
    | ANY
    | BOOLEAN
    | BYTE
    | DOUBLE
    | FALSE
    | FLOAT
    | LONG
    | NULL
    | OBJECT
    | OCTET
    | OR
    | OPTIONAL
    | RECORD
    | SEQUENCE
    | SHORT
    | SYMBOL
    | TRUE
    | UNSIGNED
    | VOID
    | argumentNameKeyword
    | bufferRelatedType
    ;

argumentNameKeyword
    : ASYNC
    | ATTRIBUTE
    | CALLBACK
    | CONST
    | CONSTRUCTOR
    | DELETER
    | DICTIONARY
    | ENUM
    | GETTER
    | INCLUDES
    | INHERIT
    | INTERFACE
    | ITERABLE
    | MAPLIKE
    | MIXIN
    | NAMESPACE
    | PARTIAL
    | READONLY
    | REQUIRED
    | SETLIKE
    | SETTER
    | STATIC
    | STRINGIFIER
    | TYPEDEF
    | UNRESTRICTED
    ;
