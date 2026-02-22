// Subset of the Web Audio API
// https://webaudio.github.io/web-audio-api/

enum OscillatorType { "sine", "square", "sawtooth", "triangle", "custom" };
enum BiquadFilterType {
  "lowpass", "highpass", "bandpass", "lowshelf",
  "highshelf", "peaking", "notch", "allpass"
};
enum ChannelCountMode { "max", "clamped-max", "explicit" };
enum ChannelInterpretation { "speakers", "discrete" };
enum DistanceModelType { "linear", "inverse", "exponential" };
enum PanningModelType { "equalpower", "HRTF" };
enum OverSampleType { "none", "2x", "4x" };

dictionary AudioNodeOptions {
  unsigned long channelCount;
  ChannelCountMode channelCountMode;
  ChannelInterpretation channelInterpretation;
};

dictionary OscillatorOptions : AudioNodeOptions {
  OscillatorType type;
  float frequency;
  float detune;
};

dictionary GainOptions : AudioNodeOptions {
  float gain;
};

dictionary DelayOptions : AudioNodeOptions {
  double maxDelayTime;
  double delayTime;
};

dictionary BiquadFilterOptions : AudioNodeOptions {
  BiquadFilterType type;
  float Q;
  float detune;
  float frequency;
  float gain;
};

dictionary PannerOptions : AudioNodeOptions {
  PanningModelType panningModel;
  DistanceModelType distanceModel;
  float positionX;
  float positionY;
  float positionZ;
  float orientationX;
  float orientationY;
  float orientationZ;
  double refDistance;
  double maxDistance;
  double rolloffFactor;
  float coneInnerAngle;
  float coneOuterAngle;
  float coneOuterGain;
};

[Exposed=Window]
interface AudioContext {
  constructor();
};

[Exposed=Window]
interface OscillatorNode {
  constructor(AudioContext context, optional OscillatorOptions options = {});
};

[Exposed=Window]
interface GainNode {
  constructor(AudioContext context, optional GainOptions options = {});
};

[Exposed=Window]
interface DelayNode {
  constructor(AudioContext context, optional DelayOptions options = {});
};

[Exposed=Window]
interface BiquadFilterNode {
  constructor(AudioContext context, optional BiquadFilterOptions options = {});
};

[Exposed=Window]
interface PannerNode {
  constructor(AudioContext context, optional PannerOptions options = {});
};
