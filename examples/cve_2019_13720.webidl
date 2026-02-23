// CVE-2019-13720: Use-after-free in Chrome ConvolverNode (Chrome 76-77)
//
// The bug is a race condition: the main thread calls SetBuffer(null)
// freeing reverb_ while the audio rendering thread is still calling
// ConvolverHandler::Process() which reads reverb_.  The missing
// MutexLocker before reverb_.reset() causes the UAF.
//
// Trigger pattern (Kaspersky PoC):
//   1. Create OfflineAudioContext(2, 0x400000, 48000)
//   2. Create ConvolverNode, ScriptProcessorNode, AudioBuffer
//   3. Connect: convolver -> scriptNode -> destination
//   4. Assign convolver.buffer = channelBuffer
//   5. Call startRendering()
//   6. Loop: convolver.buffer = null; convolver.buffer = channelBuffer

[Exposed=Window]
interface OfflineAudioContext {
  constructor(unsigned long numberOfChannels, unsigned long length, float sampleRate);
  ConvolverNode createConvolver();
  ScriptProcessorNode createScriptProcessor(
    optional unsigned long bufferSize = 4096,
    optional unsigned long numberOfInputChannels = 2,
    optional unsigned long numberOfOutputChannels = 2
  );
  AudioBuffer createBuffer(unsigned long numberOfChannels, unsigned long length, float sampleRate);
  undefined startRendering();
  readonly attribute AudioDestinationNode destination;
};

[Exposed=Window] interface ConvolverNode {
  attribute AudioBuffer? buffer;
  undefined connect(AudioNode destination);
};

[Exposed=Window] interface ScriptProcessorNode {
  undefined connect(AudioNode destination);
};

[Exposed=Window] interface AudioBuffer {};
[Exposed=Window] interface AudioDestinationNode {};
[Exposed=Window] interface AudioNode {};
