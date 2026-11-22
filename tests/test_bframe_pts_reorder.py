import pytest
import media.bframe_pts_reorder as mod

CASES = [
    ("timebase_unify", (90000, 1000)),
    ("dts_monotonic", (1, 2)),
    ("pts_offset", (1, 2)),
    ("vfr_variable", (1, 2)),
    ("zero_duration_pad", (1, 2)),
    ("gop_boundary", (1, 2)),
    ("reorder_buffer", (1, 2)),
    ("av_align", (1, 2)),
    ("timestamp_validate", (1, 2)),
    ("ctts_parse", (1, 2)),
    ("frame_index", (1, 2)),
    ("seek_restore", (1, 2)),
    ("drift_accumulate", (1.0, 2.0)),
    ("remux_order", (1, 2)),
    ("sync_offset", (0.04, 0.02)),
]

@pytest.mark.parametrize("fn_name,args", CASES)
def test_contract(fn_name, args):
    fn = getattr(mod, fn_name)
    assert fn(*args) is not None
