// Subset of the HTML Canvas API
// https://html.spec.whatwg.org/multipage/canvas.html

enum CanvasFillRule { "nonzero", "evenodd" };
enum CanvasLineCap { "butt", "round", "square" };
enum CanvasLineJoin { "round", "bevel", "miter" };
enum CanvasTextAlign { "start", "end", "left", "right", "center" };
enum CanvasDirection { "ltr", "rtl", "inherit" };
enum ImageSmoothingQuality { "low", "medium", "high" };

dictionary CanvasRenderingContext2DSettings {
  boolean alpha = true;
  boolean desynchronized = false;
};

[Exposed=Window]
interface DOMMatrix {
  constructor(optional DOMString init);
};

[Exposed=Window]
interface CanvasGradient {
  constructor();
};

[Exposed=Window]
interface CanvasPattern {
  constructor();
};

[Exposed=Window]
interface Path2D {
  constructor(optional DOMString d);
};

[Exposed=Window]
interface ImageData {
  constructor(unsigned long sw, unsigned long sh);
};

[Exposed=Window]
interface TextMetrics {
  constructor();
};
