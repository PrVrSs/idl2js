// Targeted WebIDL definitions for CVE hunting demonstration.
//
// Each definition models an API surface associated with a known browser CVE.
// The fuzzer generates randomized JS using these definitions; vulnerability
// oracles then check the output for patterns matching the original bug.

// --- CVE-2017-5112 / CVE-2016-1935: ImageData integer overflow / zero dim ---
// Chrome WebGL readPixels heap buffer overflow (uint32 wrap in sw*sh*4)
// Firefox WebGL bufferSubData zero-length buffer
[Exposed=Window]
interface ImageData {
  constructor(unsigned long sw, unsigned long sh);
};

// --- CVE-2023-1222 / CVE-2019-13720: Web Audio special float values ---
// Chrome Web Audio heap buffer overflow from Infinity/NaN in audio params
enum OscillatorType { "sine", "square", "sawtooth", "triangle", "custom" };

dictionary AudioNodeOptions {
  unsigned long channelCount;
};

dictionary OscillatorOptions : AudioNodeOptions {
  OscillatorType type;
  unrestricted float frequency;
  unrestricted float detune;
};

[Exposed=Window]
interface AudioContext {
  constructor();
};

[Exposed=Window]
interface OscillatorNode {
  constructor(AudioContext context, optional OscillatorOptions options = {});
};

// --- CVE-2024-11691 inspired: WebGL buffer config integer overflow ---
// Integer overflow in offset/stride calculations
dictionary WebGLBufferConfig {
  unsigned long offset;
  unsigned long stride;
  unsigned long count;
};

[Exposed=Window]
interface WebGLBuffer {
  constructor(optional WebGLBufferConfig config = {});
};
