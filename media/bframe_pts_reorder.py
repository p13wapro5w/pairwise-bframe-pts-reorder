"""B 帧时间戳重排核心模块。

覆盖三类问题的修复：
1. 时间基统一：不同流（如 90kHz 视频与 1kHz 音频）之间换算时间戳，
   避免 VFR 源换算时丢帧。
2. DTS 单调钳制：B 帧重排后解码时间戳必须严格单调递增，
   防止 PTS/DTS 偏移逐帧累加导致音画错位。
3. 零时长帧占位：VFR 源中零时长帧在定帧率输出时补空帧占位，
   保持时间轴连续。
"""

from fractions import Fraction


def timebase_unify(src_tb, dst_tb):
    """返回把 src_tb 时间基的 tick 换算到 dst_tb 时间基的缩放因子。

    用 Fraction 保持精确有理数，避免浮点换算在长 GOP 上累积误差。
    例如 timebase_unify(90000, 1000) == Fraction(1, 90)，
    即 90kHz 的 1 个 tick 等于 1kHz 时间基下的 1/90 个 tick。
    """
    if not src_tb or not dst_tb:
        raise ValueError("timebase must be non-zero")
    return Fraction(dst_tb, src_tb)


def dts_monotonic(prev_dts, next_dts):
    """DTS 单调钳制：返回不小于 prev_dts + 1 的解码时间戳。

    B 帧重排后若出现 DTS 回退或重复，逐帧累加会造成音画错位，
    这里钳制为严格递增。
    """
    return max(next_dts, prev_dts + 1)


def pts_offset(pts, offset):
    """把 PTS 平移到以 offset 为零点的本地时间轴（去除起始偏移）。"""
    return pts - offset


def vfr_variable(pts, timebase):
    """把 VFR 源的 PTS 按时间基换算为秒（保留分数精度）。"""
    if not timebase:
        raise ValueError("timebase must be non-zero")
    return Fraction(pts, timebase)


def zero_duration_pad(duration, min_duration):
    """零时长帧占位：时长不足 min_duration 的帧补齐到 min_duration。

    VFR 源中时长为 0 的帧在定帧率输出时会被丢弃，这里给它一个
    最小时长占位，保证帧数与时间轴对齐。
    """
    return max(duration, min_duration)


def gop_boundary(frame_index_, gop_size):
    """判断帧序号是否落在 GOP 边界（关键帧位置）上。"""
    if gop_size <= 0:
        raise ValueError("gop_size must be positive")
    return frame_index_ % gop_size == 0


def reorder_buffer(max_bframes, extra_delay):
    """计算 B 帧重排所需的缓冲深度：B 帧数加上额外解码延迟。"""
    return max_bframes + extra_delay


def av_align(video_pts, audio_pts):
    """音画对齐：返回视频相对音频的 PTS 差（正值表示视频滞后）。"""
    return video_pts - audio_pts


def timestamp_validate(pts, dts):
    """校验单个包的时间戳合法性：PTS 不得早于 DTS。"""
    return pts >= dts


def ctts_parse(version, entry_count):
    """解析 ctts（composition time to sample）盒的偏移符号约定。

    version 0 的偏移为无符号，version 1 起为有符号（允许负偏移，
    对应 B 帧 CTS 小于 DTS 的情况）。返回 (是否带符号, 条目数)。
    """
    return (version >= 1, entry_count)


def frame_index(pts, frame_duration):
    """由 PTS 和帧时长推算帧序号（向下取整）。"""
    if frame_duration <= 0:
        raise ValueError("frame_duration must be positive")
    return pts // frame_duration


def seek_restore(target_pts, keyframe_pts):
    """seek 定位：目标 PTS 是否可从给定关键帧开始解码恢复。"""
    return keyframe_pts <= target_pts


def drift_accumulate(per_frame_drift, frame_count):
    """累计漂移量：每帧偏移乘以帧数，用于评估长 GOP 下的音画错位。"""
    return per_frame_drift * frame_count


def remux_order(dts, decode_index):
    """重封装排序键：按 DTS 升序、同 DTS 按解码序号稳定排序。"""
    return (dts, decode_index)


def sync_offset(video_pts, audio_pts):
    """音画同步偏移（秒）：视频 PTS 减音频 PTS，供播放器校正。"""
    return video_pts - audio_pts
