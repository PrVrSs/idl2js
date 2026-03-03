from dataclasses import dataclass, field
from typing import Callable

from z3 import And, Int, Or, Real


UINT32_MAX = 0xFFFF_FFFF
INT32_MAX = 0x7FFF_FFFF
INT64_BOUNDARY = 1 << 62
UINT64_BOUNDARY = 1 << 62
MAX_AUDIO_CHANNELS = 32
MIN_OVERFLOW_LENGTH = UINT32_MAX // (4 * MAX_AUDIO_CHANNELS) + 1
MIN_DECODE_DIMENSION = 1024


@dataclass(frozen=True)
class OraclePredicate:
    """A vulnerability predicate that can be solved by Z3.

    Attributes:
        name: identifier (typically a CVE ID or bug class name).
        target_type: the WebIDL type this predicate applies to.
        fields: mapping of field names to their IDL type names.
        formula_fn: callable(vars_dict) -> z3 BoolRef.
    """
    name: str
    target_type: str
    fields: dict = field(default_factory=dict)
    formula_fn: Callable = field(default=lambda _: True)


# ---------------------------------------------------------------------------
# CVE-2024-4559: AudioBuffer heap overflow
# numberOfChannels × length × 4 > UINT32_MAX
# ---------------------------------------------------------------------------

def _audio_buffer_overflow(v):
    n_ch = v['numberOfChannels']
    length = v['length']
    return And(
        n_ch >= 1,
        n_ch <= MAX_AUDIO_CHANNELS,
        length >= MIN_OVERFLOW_LENGTH,
        n_ch * length * 4 > UINT32_MAX,
    )


AUDIO_BUFFER_OVERFLOW = OraclePredicate(
    name='CVE-2024-4559',
    target_type='AudioBuffer',
    fields={
        'numberOfChannels': 'unsigned long',
        'length': 'unsigned long',
        'sampleRate': 'float',
    },
    formula_fn=_audio_buffer_overflow,
)


# ---------------------------------------------------------------------------
# CVE-2024-2886: WebCodecs timestamp overflow
# |timestamp| >= 2^62
# ---------------------------------------------------------------------------

def _webcodecs_timestamp(v):
    ts = v['timestamp']
    return Or(ts >= INT64_BOUNDARY, ts <= -INT64_BOUNDARY)


WEBCODECS_TIMESTAMP = OraclePredicate(
    name='CVE-2024-2886-timestamp',
    target_type='EncodedVideoChunk',
    fields={'timestamp': 'long long'},
    formula_fn=_webcodecs_timestamp,
)


# ---------------------------------------------------------------------------
# CVE-2024-2886: WebCodecs large dimensions
# codedWidth >= 1024 AND codedHeight >= 1024
# ---------------------------------------------------------------------------

def _webcodecs_large_dims(v):
    w = v['codedWidth']
    h = v['codedHeight']
    return And(w >= MIN_DECODE_DIMENSION, h >= MIN_DECODE_DIMENSION)


WEBCODECS_LARGE_DIMS = OraclePredicate(
    name='CVE-2024-2886-dimensions',
    target_type='VideoDecoderConfig',
    fields={
        'codedWidth': 'unsigned long',
        'codedHeight': 'unsigned long',
    },
    formula_fn=_webcodecs_large_dims,
)


# ---------------------------------------------------------------------------
# CVE-2024-5499: Streams highWaterMark overflow
# highWaterMark > INT32_MAX/2 or highWaterMark < 0
# ---------------------------------------------------------------------------

def _streams_hwm_overflow(v):
    hwm = v['highWaterMark']
    return Or(hwm > INT32_MAX // 2, hwm < 0)


STREAMS_HWM_OVERFLOW = OraclePredicate(
    name='CVE-2024-5499',
    target_type='ByteLengthQueuingStrategy',
    fields={'highWaterMark': 'double'},
    formula_fn=_streams_hwm_overflow,
)


# ---------------------------------------------------------------------------
# WebNN: tensor dimension overflow
# dim0 × dim1 × dtype_bytes > UINT32_MAX
# ---------------------------------------------------------------------------

def _webnn_overflow(v):
    d0 = v['dim0']
    d1 = v['dim1']
    return And(d0 >= 1, d1 >= 1, d0 * d1 * 4 > UINT32_MAX)


WEBNN_OVERFLOW = OraclePredicate(
    name='webnn-tensor-overflow',
    target_type='MLOperandDescriptor',
    fields={
        'dim0': 'unsigned long',
        'dim1': 'unsigned long',
    },
    formula_fn=_webnn_overflow,
)


# ---------------------------------------------------------------------------
# OffscreenCanvas: width × height × 4 > UINT32_MAX
# ---------------------------------------------------------------------------

def _offscreen_canvas_overflow(v):
    w = v['width']
    h = v['height']
    return And(w > 0, h > 0, w * h * 4 > UINT32_MAX)


OFFSCREEN_CANVAS_OVERFLOW = OraclePredicate(
    name='offscreen-canvas-overflow',
    target_type='OffscreenCanvas',
    fields={
        'width': 'unsigned long',
        'height': 'unsigned long',
    },
    formula_fn=_offscreen_canvas_overflow,
)


# ---------------------------------------------------------------------------
# WebTransport: sendOrder near INT64 boundary
# |sendOrder| >= 2^62
# ---------------------------------------------------------------------------

def _webtransport_sendorder(v):
    so = v['sendOrder']
    return Or(so >= INT64_BOUNDARY, so <= -INT64_BOUNDARY)


WEBTRANSPORT_SENDORDER = OraclePredicate(
    name='webtransport-sendOrder',
    target_type='WebTransportSendStreamOptions',
    fields={'sendOrder': 'long long'},
    formula_fn=_webtransport_sendorder,
)


# ---------------------------------------------------------------------------
# File System Access: offset >= 2^62
# ---------------------------------------------------------------------------

def _file_system_at_overflow(v):
    at = v['at']
    return at >= UINT64_BOUNDARY


FILE_SYSTEM_AT_OVERFLOW = OraclePredicate(
    name='file-system-at-overflow',
    target_type='FileSystemReadWriteOptions',
    fields={'at': 'unsigned long long'},
    formula_fn=_file_system_at_overflow,
)


# ---------------------------------------------------------------------------
# WebRTC DataChannel: maxPacketLifeTime >= 60000
# ---------------------------------------------------------------------------

def _webrtc_datachannel(v):
    mpl = v['maxPacketLifeTime']
    return mpl >= 60000


WEBRTC_DATACHANNEL = OraclePredicate(
    name='webrtc-datachannel-overflow',
    target_type='RTCDataChannelInit',
    fields={'maxPacketLifeTime': 'unsigned short'},
    formula_fn=_webrtc_datachannel,
)


# ---------------------------------------------------------------------------
# Media Insertable: VideoFrame timestamp overflow
# |timestamp| >= 2^62
# ---------------------------------------------------------------------------

def _media_insertable_timestamp(v):
    ts = v['timestamp']
    return Or(ts >= INT64_BOUNDARY, ts <= -INT64_BOUNDARY)


MEDIA_INSERTABLE_TIMESTAMP = OraclePredicate(
    name='media-insertable-timestamp',
    target_type='VideoFrame',
    fields={'timestamp': 'long long'},
    formula_fn=_media_insertable_timestamp,
)


# ---------------------------------------------------------------------------
# VideoFrame: dimension overflow
# codedWidth × codedHeight × 4 (RGBA) > UINT32_MAX
# Firefox allocates pixel buffers based on dimensions — no V8 sandbox protection
# ---------------------------------------------------------------------------

def _videoframe_dims_overflow(v):
    w = v['codedWidth']
    h = v['codedHeight']
    return And(w >= 1, h >= 1, w * h * 4 > UINT32_MAX)


VIDEOFRAME_DIMS_OVERFLOW = OraclePredicate(
    name='videoframe-dims-overflow',
    target_type='VideoFrameInit',
    fields={
        'codedWidth': 'unsigned long',
        'codedHeight': 'unsigned long',
        'timestamp': 'long long',
    },
    formula_fn=_videoframe_dims_overflow,
)


# ---------------------------------------------------------------------------
# VideoFrame: timestamp INT64 overflow
# |timestamp| >= 2^62 — same class as EncodedVideoChunk but on VideoFrame
# ---------------------------------------------------------------------------

def _videoframe_timestamp(v):
    ts = v['timestamp']
    return Or(ts >= INT64_BOUNDARY, ts <= -INT64_BOUNDARY)


VIDEOFRAME_TIMESTAMP = OraclePredicate(
    name='videoframe-timestamp-overflow',
    target_type='VideoFrameInit',
    fields={'timestamp': 'long long'},
    formula_fn=_videoframe_timestamp,
)


# ---------------------------------------------------------------------------
# AudioData: allocation overflow
# numberOfFrames × numberOfChannels × bytesPerSample > UINT32_MAX
# s32/f32 = 4 bytes; s16 = 2 bytes
# ---------------------------------------------------------------------------

def _audiodata_overflow(v):
    frames = v['numberOfFrames']
    channels = v['numberOfChannels']
    return And(frames >= 1, channels >= 1, frames * channels * 4 > UINT32_MAX)


AUDIODATA_OVERFLOW = OraclePredicate(
    name='audiodata-alloc-overflow',
    target_type='AudioDataInit',
    fields={
        'numberOfFrames': 'unsigned long',
        'numberOfChannels': 'unsigned long',
    },
    formula_fn=_audiodata_overflow,
)


# ---------------------------------------------------------------------------
# AudioData: timestamp overflow
# ---------------------------------------------------------------------------

def _audiodata_timestamp(v):
    ts = v['timestamp']
    return Or(ts >= INT64_BOUNDARY, ts <= -INT64_BOUNDARY)


AUDIODATA_TIMESTAMP = OraclePredicate(
    name='audiodata-timestamp-overflow',
    target_type='AudioDataInit',
    fields={'timestamp': 'long long'},
    formula_fn=_audiodata_timestamp,
)


# ---------------------------------------------------------------------------
# EncodedAudioChunk: timestamp overflow (audio path)
# Same INT64 class as video, but Firefox audio decoder has separate code path
# ---------------------------------------------------------------------------

def _encoded_audio_timestamp(v):
    ts = v['timestamp']
    return Or(ts >= INT64_BOUNDARY, ts <= -INT64_BOUNDARY)


ENCODED_AUDIO_TIMESTAMP = OraclePredicate(
    name='encoded-audio-timestamp-overflow',
    target_type='EncodedAudioChunkInit',
    fields={'timestamp': 'long long'},
    formula_fn=_encoded_audio_timestamp,
)


# ---------------------------------------------------------------------------
# VideoEncoderConfig: dimension overflow in encoder pipeline
# width × height × bytesPerPixel overflow in encoder buffer allocation
# ---------------------------------------------------------------------------

def _video_encoder_dims(v):
    w = v['width']
    h = v['height']
    return And(w >= 1, h >= 1, w * h * 4 > UINT32_MAX)


VIDEO_ENCODER_DIMS_OVERFLOW = OraclePredicate(
    name='video-encoder-dims-overflow',
    target_type='VideoEncoderConfig',
    fields={
        'width': 'unsigned long',
        'height': 'unsigned long',
    },
    formula_fn=_video_encoder_dims,
)


# ---------------------------------------------------------------------------
# WebGPU: buffer size near allocation boundaries
# size >= 2^31 (triggers 32-bit truncation if cast to int)
# ---------------------------------------------------------------------------

def _gpu_buffer_overflow(v):
    size = v['size']
    return And(size >= (1 << 31), size <= UINT32_MAX)


GPU_BUFFER_OVERFLOW = OraclePredicate(
    name='webgpu-buffer-overflow',
    target_type='GPUBufferDescriptor',
    fields={'size': 'unsigned long long'},
    formula_fn=_gpu_buffer_overflow,
)


# ---------------------------------------------------------------------------
# WebGPU: texture dimensions overflow
# width × height × depthOrArrayLayers × bytesPerPixel > UINT32_MAX
# (rgba8 = 4 bytes/pixel, rgba32float = 16 bytes/pixel)
# ---------------------------------------------------------------------------

def _gpu_texture_overflow(v):
    w = v['width']
    h = v['height']
    d = v['depthOrArrayLayers']
    return And(w >= 1, h >= 1, d >= 1, w * h * d * 4 > UINT32_MAX)


GPU_TEXTURE_OVERFLOW = OraclePredicate(
    name='webgpu-texture-overflow',
    target_type='GPUExtent3DDict',
    fields={
        'width': 'unsigned long',
        'height': 'unsigned long',
        'depthOrArrayLayers': 'unsigned long',
    },
    formula_fn=_gpu_texture_overflow,
)


# ---------------------------------------------------------------------------
# WebGPU: texel copy layout overflow
# offset + bytesPerRow × rowsPerImage can overflow
# ---------------------------------------------------------------------------

def _gpu_texel_copy_overflow(v):
    offset = v['offset']
    bpr = v['bytesPerRow']
    rpi = v['rowsPerImage']
    return And(
        bpr >= 256,
        rpi >= 1,
        offset + bpr * rpi > UINT32_MAX,
    )


GPU_TEXEL_COPY_OVERFLOW = OraclePredicate(
    name='webgpu-texelcopy-overflow',
    target_type='GPUTexelCopyBufferLayout',
    fields={
        'offset': 'unsigned long long',
        'bytesPerRow': 'unsigned long',
        'rowsPerImage': 'unsigned long',
    },
    formula_fn=_gpu_texel_copy_overflow,
)


# ---------------------------------------------------------------------------
# WebGPU: vertex buffer stride overflow
# arrayStride × vertexCount can exceed allocation
# ---------------------------------------------------------------------------

def _gpu_vertex_stride_overflow(v):
    stride = v['arrayStride']
    return stride >= (1 << 31)


GPU_VERTEX_STRIDE_OVERFLOW = OraclePredicate(
    name='webgpu-vertex-stride-overflow',
    target_type='GPUVertexBufferLayout',
    fields={'arrayStride': 'unsigned long long'},
    formula_fn=_gpu_vertex_stride_overflow,
)


# ---------------------------------------------------------------------------
# WebGPU: buffer binding offset + size overflow
# offset + size > UINT32_MAX
# ---------------------------------------------------------------------------

def _gpu_buffer_binding_overflow(v):
    offset = v['offset']
    size = v['size']
    return And(offset >= 1, size >= 1, offset + size > UINT32_MAX)


GPU_BUFFER_BINDING_OVERFLOW = OraclePredicate(
    name='webgpu-buffer-binding-overflow',
    target_type='GPUBufferBinding',
    fields={
        'offset': 'unsigned long long',
        'size': 'unsigned long long',
    },
    formula_fn=_gpu_buffer_binding_overflow,
)


PREDICATES = [
    AUDIO_BUFFER_OVERFLOW,
    WEBCODECS_TIMESTAMP,
    WEBCODECS_LARGE_DIMS,
    STREAMS_HWM_OVERFLOW,
    WEBNN_OVERFLOW,
    OFFSCREEN_CANVAS_OVERFLOW,
    WEBTRANSPORT_SENDORDER,
    FILE_SYSTEM_AT_OVERFLOW,
    WEBRTC_DATACHANNEL,
    MEDIA_INSERTABLE_TIMESTAMP,
    VIDEOFRAME_DIMS_OVERFLOW,
    VIDEOFRAME_TIMESTAMP,
    AUDIODATA_OVERFLOW,
    AUDIODATA_TIMESTAMP,
    ENCODED_AUDIO_TIMESTAMP,
    VIDEO_ENCODER_DIMS_OVERFLOW,
    GPU_BUFFER_OVERFLOW,
    GPU_TEXTURE_OVERFLOW,
    GPU_TEXEL_COPY_OVERFLOW,
    GPU_VERTEX_STRIDE_OVERFLOW,
    GPU_BUFFER_BINDING_OVERFLOW,
]


def predicates_for_type(target_type):
    """Return all predicates applicable to a given WebIDL type."""
    return [p for p in PREDICATES if p.target_type == target_type]
