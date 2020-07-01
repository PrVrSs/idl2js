# *WIP* idl2js

### Examples

```
[Exposed=(Window,Worker)]
interface Blob {
  [Throws]
  constructor(optional sequence<BlobPart> blobParts,
              optional BlobPropertyBag options = {});

  [GetterThrows]
  readonly attribute unsigned long long size;

  readonly attribute DOMString type;
};
```

```
let v_db181039fd784c4c95f9dbcabe341d84 = new Blob()
let v_25807798757b479782978804d68e3679 = v_db181039fd784c4c95f9dbcabe341d84.size
let v_669e4816ca6f4bc59a5ec224b5ce1dbd = v_db181039fd784c4c95f9dbcabe341d84.type
```


### Links

* [searchfox - webidl](https://searchfox.org/mozilla-central/source/dom/webidl)
