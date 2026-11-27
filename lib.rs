//! C ABI over neteq-core for the AflatoonSuite tweak.
//! One handle = one speaker (uid). Frames are 10 ms mono PCM16.
use neteq_core::{AudioPacket, DelayManagerConfig, NetEq, NetEqConfig, NetEqOperation};
use std::os::raw::c_int;
use std::panic::{catch_unwind, AssertUnwindSafe};

pub struct AflNetEq {
    eq: NetEq,
    frame: usize,
    ts: u32,
    seq: u16,
}

fn op_code(op: NetEqOperation) -> c_int {
    match op {
        NetEqOperation::Normal => 0,
        NetEqOperation::Accelerate => 1,
        NetEqOperation::PreemptiveExpand => 2,
        NetEqOperation::Expand => 3,
        NetEqOperation::ComfortNoise => 4,
        NetEqOperation::Merge => 5,
    }
}

/// min/max_delay_frames: jitter-buffer target bounds in 10 ms frames.
/// Use (1, 2) for zero added latency (PLC / merge / comfort noise only);
/// larger max lets NetEQ stretch/accelerate but adds latency.
#[no_mangle]
pub extern "C" fn afl_neteq_new(sample_rate: c_int, min_delay_frames: c_int, max_delay_frames: c_int) -> *mut AflNetEq {
    let r = catch_unwind(|| {
        if !(8000..=48000).contains(&sample_rate) {
            return std::ptr::null_mut();
        }
        let min_d = min_delay_frames.max(0) as usize;
        let max_d = (max_delay_frames.max(min_delay_frames.max(1))) as usize;
        let mut cfg = NetEqConfig::default();
        cfg.sample_rate = sample_rate as u32;
        cfg.channels = 1;
        cfg.frame_size_ms = 10;
        cfg.delay_config = DelayManagerConfig { min_delay_frames: min_d, max_delay_frames: max_d, percentile: 0.95 };
        cfg.decision_config.timestamp_tolerance = (sample_rate as u32) / 100;
        match NetEq::new(cfg) {
            Ok(eq) => Box::into_raw(Box::new(AflNetEq { eq, frame: (sample_rate as usize) / 100, ts: 0, seq: 0 })),
            Err(_) => std::ptr::null_mut(),
        }
    });
    r.unwrap_or(std::ptr::null_mut())
}

/// Process one 10 ms frame. `lost` != 0 means the frame did not arrive:
/// nothing is inserted, the timeline advances, and NetEQ conceals it (PLC).
/// Returns the NetEQ operation code (0 normal, 1 accel, 2 expand-preemptive,
/// 3 PLC, 4 comfort noise, 5 merge) or -1 on bad arguments / internal error.
#[no_mangle]
pub unsafe extern "C" fn afl_neteq_process(h: *mut AflNetEq, input: *const i16, output: *mut i16, n: c_int, lost: c_int) -> c_int {
    if h.is_null() || output.is_null() || n <= 0 {
        return -1;
    }
    let s = &mut *h;
    if n as usize != s.frame || (lost == 0 && input.is_null()) {
        return -1;
    }
    let r = catch_unwind(AssertUnwindSafe(|| {
        if lost == 0 {
            let pcm = std::slice::from_raw_parts(input, s.frame).to_vec();
            let _ = s.eq.insert_packet(AudioPacket::new(s.ts, s.seq, pcm));
        }
        s.ts = s.ts.wrapping_add(s.frame as u32);
        s.seq = s.seq.wrapping_add(1);
        let out = std::slice::from_raw_parts_mut(output, s.frame);
        match s.eq.get_audio(out) {
            Ok(op) => op_code(op),
            Err(_) => -1,
        }
    }));
    r.unwrap_or(-1)
}

#[no_mangle]
pub unsafe extern "C" fn afl_neteq_reset(h: *mut AflNetEq) {
    if h.is_null() { return; }
    let s = &mut *h;
    let _ = catch_unwind(AssertUnwindSafe(|| { s.eq.reset(); s.ts = 0; s.seq = 0; }));
}

#[no_mangle]
pub unsafe extern "C" fn afl_neteq_free(h: *mut AflNetEq) {
    if !h.is_null() { drop(Box::from_raw(h)); }
}
