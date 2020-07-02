[Exposed=(Window,Worker)]
interface Blob {
  [Throws]
  constructor(optional sequence<BlobPart> blobParts,
              optional BlobPropertyBag options = {});

  [GetterThrows]
  readonly attribute unsigned long long size;

  readonly attribute DOMString type;

  [Throws]
  Blob slice(optional [Clamp] long long start,
             optional [Clamp] long long end,
             optional DOMString contentType);

  [NewObject, Throws] ReadableStream stream();
  [NewObject] Promise<USVString> text();
  [NewObject] Promise<ArrayBuffer> arrayBuffer();
};
