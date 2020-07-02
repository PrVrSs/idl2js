lexer grammar WebIDLLexer;

channels { ERROR }

WHITESPACE:                          [\t\n\r ]+                         -> channel(HIDDEN);
COMMENT:                             ('//'~[\n\r]*|'/*'(.|'\n')*?'*/')+ -> channel(HIDDEN);

EQUAL_SYMBOL:                        '=';
QUESTION_SYMBOL:                     '?';
LEFT_PAREN:                          '(';
RIGHT_PAREN:                         ')';
LEFT_BRACKET:                        '[';
RIGHT_BRACKET:                       ']';
LEFT_BRACE:                          '{';
RIGHT_BRACE:                         '}';
LEFT_ANGLE:                          '<';
RIGHT_ANGLE:                         '>';
COMMA:                               ',';
SEMI:                                ';';
COLON:                               ':';
MINUS:                               '-';
ELLIPSIS:                            '...';
DOT:                                 '.';

// Keywords

ANY:                                 'any';
ASYNC:                               'async';
ATTRIBUTE:                           'attribute';
BOOLEAN:                             'boolean';
BYTE:                                'byte';
BYTE_STRING:                         'ByteString';
CALLBACK:                            'callback';
CONST:                               'const';
CONSTRUCTOR:                         'constructor';
DELETER:                             'deleter';
DICTIONARY:                          'dictionary';
DOM_STRING:                          'DOMString';
DOUBLE:                              'double';
ENUM:                                'enum';
FALSE:                               'false';
FLOAT:                               'float';
FROZEN_ARRAY:                        'FrozenArray';
GETTER:                              'getter';
INFINITY:                            'Infinity';
INCLUDES:                            'includes';
INHERIT:                             'inherit';
INTERFACE:                           'interface';
ITERABLE:                            'iterable';
LONG:                                'long';
MAPLIKE:                             'maplike';
MINUS_INFINITY:                      '-Infinity';
MIXIN:                               'mixin';
NAMESPACE:                           'namespace';
NAN:                                 'NaN';
NULL:                                'null';
OBJECT:                              'object';
OBSERVABLE_ARRAY:                    'ObservableArray';
OCTET:                               'octet';
OPTIONAL:                            'optional';
OR:                                  'or';
PARTIAL:                             'partial';
PROMISE:                             'Promise';
READONLY:                            'readonly';
RECORD:                              'record';
REQUIRED:                            'required';
SEQUENCE:                            'sequence';
SETLIKE:                             'setlike';
SETTER:                              'setter';
SHORT:                               'short';
STATIC:                              'static';
STRINGIFIER:                         'stringifier';
SYMBOL:                              'symbol';
TRUE:                                'true';
TYPEDEF:                             'typedef';
UNRESTRICTED:                        'unrestricted';
UNSIGNED:                            'unsigned';
USV_STRING:                          'USVString';
VOID:                                'void';

// bufferRelatedType

ARRAY_BUFFER:                        'ArrayBuffer';
DATA_VIEW:                           'DataView';
INT_8_ARRAY:                         'Int8Array';
INT_16_ARRAY:                        'Int16Array';
INT_32_ARRAY:                        'Int32Array';
UINT_8_ARRAY:                        'Uint8Array';
UINT_16_ARRAY:                       'Uint16Array';
UINT_32_ARRAY:                       'Uint32Array';
UINT_8_CLAMPED_ARRAY:                'Uint8ClampedArray';
FLOAT_32_ARRAY:                      'Float32Array';
FLOAT_64_ARRAY:                      'Float64Array';

IntegerLiteral
    :                                '-'? HexIntegerLiteral
    |                                '-'? OctalIntegerLiteral
    |                                '-'? DecimalIntegerLiteral
    ;

DecimalLiteral
    :                                '-'? [0-9]+ '.' [0-9]* ExponentPart?
    |                                '-'? '.' [0-9]+ ExponentPart?
    |                                '-'? [0-9]+ ExponentPart
    ;

StringLiteral:                       '"' DoubleStringCharacter* '"';

HexIntegerLiteral:                   '0' [xX] HexDigit+;
OctalIntegerLiteral:                 '0' [0-7]+;
DecimalIntegerLiteral
    :                                '0'
    |                                [1-9] [0-9]*
    ;

IDENTIFIER
    : [_-]?[A-Za-z][0-9A-Z_a-z-]*
    ;

OTHER
    : ~[\t\n\r 0-9A-Z_a-z]
    ;

// Fragment rules

fragment DoubleStringCharacter
    : ~["\\\r\n]
    ;

fragment HexDigit
    : [0-9a-fA-F]
    ;

fragment ExponentPart
    : [eE] [+-]? [0-9]+
    ;
