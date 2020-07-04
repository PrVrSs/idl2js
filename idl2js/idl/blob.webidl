typedef (BufferSource or Blob or USVString) BlobPart;

[Exposed=(Window,Worker)]
interface Blob {
  [Throws]
  constructor(optional sequence<BlobPart> blobParts,
              optional BlobPropertyBag options = {});

  [GetterThrows]
  readonly attribute unsigned long long size;

  readonly attribute DOMString type;

  //slice Blob into byte-ranged chunks

  [Throws]
  Blob slice(optional [Clamp] long long start,
             optional [Clamp] long long end,
             optional DOMString contentType);

  // read from the Blob.
  [NewObject, Throws] ReadableStream stream();
  [NewObject] Promise<USVString> text();
  [NewObject] Promise<ArrayBuffer> arrayBuffer();
};

enum EndingType { "transparent", "native" };

dictionary BlobPropertyBag {
  DOMString type = "";
  EndingType endings = "transparent";
};

partial interface Blob {
  // This returns the type of BlobImpl used for this Blob.
  [ChromeOnly]
  readonly attribute DOMString blobImplType;
};
