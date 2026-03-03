// WebGPU — high-value fuzzing surface
// Focus: buffer sizes, texture dimensions, copy offsets — integer overflow territory
//
// Key CVEs: CVE-2025-10500 (UAF Dawn), CVE-2025-12725 (OOB write),
//           CVE-2025-14765 (UAF heap corruption), CVE-2026-3062 (Tint)

dictionary GPUExtent3DDict {
    required unsigned long width;
    unsigned long height = 1;
    unsigned long depthOrArrayLayers = 1;
};

enum GPUTextureDimension { "1d", "2d", "3d" };

enum GPUTextureFormat {
    "r8unorm", "r8snorm", "r8uint", "r8sint",
    "r16uint", "r16sint", "r16float",
    "rg8unorm", "rg8snorm", "rg8uint", "rg8sint",
    "r32uint", "r32sint", "r32float",
    "rg16uint", "rg16sint", "rg16float",
    "rgba8unorm", "rgba8unorm-srgb", "rgba8snorm", "rgba8uint", "rgba8sint",
    "bgra8unorm", "bgra8unorm-srgb",
    "rg32uint", "rg32sint", "rg32float",
    "rgba16uint", "rgba16sint", "rgba16float",
    "rgba32uint", "rgba32sint", "rgba32float",
    "depth16unorm", "depth24plus", "depth24plus-stencil8", "depth32float",
    "stencil8", "depth32float-stencil8"
};

[Exposed=(Window, Worker)]
interface GPUBuffer {
    constructor(GPUBufferDescriptor descriptor);
};

dictionary GPUBufferDescriptor {
    required unsigned long long size;
    required unsigned long usage;
    boolean mappedAtCreation = false;
};

[Exposed=(Window, Worker)]
interface GPUTexture {
    constructor(GPUTextureDescriptor descriptor);
};

dictionary GPUTextureDescriptor {
    required GPUExtent3DDict size;
    unsigned long mipLevelCount = 1;
    unsigned long sampleCount = 1;
    GPUTextureDimension dimension = "2d";
    required GPUTextureFormat format;
    required unsigned long usage;
};

dictionary GPUTexelCopyBufferLayout {
    unsigned long long offset = 0;
    unsigned long bytesPerRow;
    unsigned long rowsPerImage;
};

dictionary GPUOrigin3DDict {
    unsigned long x = 0;
    unsigned long y = 0;
    unsigned long z = 0;
};

[Exposed=(Window, Worker)]
interface GPUQuerySet {
    constructor(GPUQuerySetDescriptor descriptor);
};

enum GPUQueryType { "occlusion", "timestamp" };

dictionary GPUQuerySetDescriptor {
    required GPUQueryType type;
    required unsigned long count;
};

dictionary GPUVertexAttribute {
    required unsigned long long offset;
    required unsigned long shaderLocation;
};

dictionary GPUVertexBufferLayout {
    required unsigned long long arrayStride;
    sequence<GPUVertexAttribute> attributes;
};

dictionary GPUMultisampleState {
    unsigned long count = 1;
    unsigned long mask = 4294967295;
    boolean alphaToCoverageEnabled = false;
};

dictionary GPURenderPassDescriptor {
    unsigned long long maxDrawCount = 50000000;
};

dictionary GPUBufferBinding {
    unsigned long long offset = 0;
    unsigned long long size;
};

[Exposed=(Window, Worker)]
interface GPUCanvasContext {
    constructor(GPUCanvasConfiguration configuration);
};

dictionary GPUCanvasConfiguration {
    required GPUTextureFormat format;
    unsigned long usage = 16;
};

enum GPUAddressMode { "clamp-to-edge", "repeat", "mirror-repeat" };
enum GPUFilterMode { "nearest", "linear" };
enum GPUMipmapFilterMode { "nearest", "linear" };

[Exposed=(Window, Worker)]
interface GPUSampler {
    constructor(GPUSamplerDescriptor descriptor);
};

dictionary GPUSamplerDescriptor {
    GPUAddressMode addressModeU = "clamp-to-edge";
    GPUAddressMode addressModeV = "clamp-to-edge";
    GPUAddressMode addressModeW = "clamp-to-edge";
    GPUFilterMode magFilter = "nearest";
    GPUFilterMode minFilter = "nearest";
    GPUMipmapFilterMode mipmapFilter = "nearest";
    float lodMinClamp = 0;
    float lodMaxClamp = 32;
    unsigned short maxAnisotropy = 1;
};
