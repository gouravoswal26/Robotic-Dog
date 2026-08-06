#!/usr/bin/env python3
"""
voice_control.py — Lightweight, low-latency voice control pipeline for a
quadruped robot running on Jetson Orin Nano 8GB, alongside YOLO (GPU) and
an RL locomotion policy (GPU).

Pipeline
--------
    mic (INMP441, hw:APE,0) --> [resample 48kHz/stereo/int32 -> 16kHz mono int16]
              |
              v
         [openWakeWord]  (always-on, CPU, ~1-3% load)
              |
              v  (wake word detected)
         [webrtcvad end-pointed recording]  (CPU, cheap)
              |
              v  (speech captured)
         [whisper.cpp / pywhispercpp]  (CPU, loaded once, quantized model)
              |
              v
         [intent parser] --> dispatch_command() --> hook into your ROS2 /
                                                      ReAct agent loop

Microphone hardware notes (Jetson Orin Nano + INMP441, confirmed by hand)
--------------------------------------------------------------------------
`arecord -l` shows the mic on card "APE" (the Tegra Audio Processing Engine
XBAR), device 0, routed I2S2 -> ADMAIF1. Testing with `arecord` confirmed
this device only reliably captures:
    - 48000 Hz
    - 2 channels (interleaved stereo, even though the INMP441 is physically
      mono — the mic's output is present on one or both channels depending
      on how L/R was strapped)
    - S32_LE (32-bit signed samples)

It does NOT support opening directly at 16 kHz / mono / 16-bit the way the
original version of this script assumed. Instead of asking ALSA/PortAudio
to do that conversion (which is unreliable across systems and was part of
why earlier recordings sounded quiet/garbled), this script captures the
mic's *native* format and does its own resampling down to what
openWakeWord / webrtcvad / whisper.cpp actually want: 16 kHz mono int16.

If a hardware decoupling capacitor (0.1uF across VDD/GND, right at the
INMP441 breakout) was missing, you'd also see a constant hum line and
periodic full-scale spikes in the captured audio (visible on a spectrogram)
— that's an electrical/wiring issue, not something this script can fix in
software, but it's mentioned here since it's the other half of getting a
clean signal into this pipeline.

Design choices made for efficiency on a shared Jetson Orin Nano 8GB
------------------------------------------------------------------
1. Everything in this file runs on CPU only. GPU memory/engines are left
   entirely free for your TensorRT YOLO model and your RL policy.
2. openWakeWord only runs while idle. As soon as a wake word fires, wake
   word inference is paused (no wasted compute) while we record + transcribe.
3. Audio is captured once, in one small (10 ms) callback-driven stream, and
   is fanned out to both openWakeWord (which wants 80 ms = 1280-sample
   multiples) and webrtcvad (which wants 10/20/30 ms frames). No duplicate
   streams.
4. The native-rate capture is resampled to 16 kHz mono int16 inside the
   audio callback itself (cheap: a short FIR anti-alias filter + 3:1
   decimation), so everything downstream is unchanged from a "normal"
   16 kHz mic and stays simple.
5. The Whisper model is loaded exactly once and kept resident for the life
   of the process (no per-utterance subprocess spawn / model reload).
6. Silence (VAD) end-pointing means we send whisper.cpp the *shortest*
   possible clip that contains the full command, instead of a fixed-length
   window — this is the single biggest lever on latency + CPU cost for
   short-command STT.
7. A "no speech after wake word" timeout aborts before ever calling
   whisper, so a false wake-word trigger costs ~0 extra compute.
8. The audio callback thread never blocks and never does heavy work — it
   only does the resample math and pushes bytes onto a bounded queue. If
   the consumer ever falls behind, we drop the oldest audio rather than
   causing input-stream overruns.
9. whisper.cpp's encoder cost scales with `audio_ctx` (its internal context
   window), which defaults to 1500 (~30s worth of context) regardless of how
   short your actual clip is. For short commands we explicitly shrink this
   (see Transcriber / --audio-ctx), which is the single biggest lever on
   whisper inference latency for short utterances — much bigger than model
   size alone.

Install (on the Jetson, inside your existing Python env)
----------------------------------------------------------
    pip install sounddevice numpy scipy openwakeword webrtcvad-wheels

    # scipy is used only for the small FIR anti-alias filter used to
    # resample the mic's native 48kHz capture down to 16kHz.

    # onnxruntime: openWakeWord needs onnxruntime. On Jetson, install
    # NVIDIA's aarch64 wheel for your JetPack version rather than the
    # generic PyPI one:
    #   https://elinux.org/Jetson_Zoo#ONNX_Runtime
    # (CPU-only onnxruntime is fine here — openWakeWord's models are tiny.)

    # pywhispercpp: build WITHOUT CUDA so it stays on CPU and does not
    # compete with YOLO/RL for GPU memory. This is what actually keeps
    # whisper off the GPU — there is no reliable "use_gpu" constructor
    # kwarg to rely on instead, so the build flag below is required:
    #   GGML_CUDA=0 pip install pywhispercpp
    # (pywhispercpp will fetch/build whisper.cpp for you the first time.)

    # Both models are loaded from local files, no download needed:
    #   - wake word: WAKEWORD_MODEL_PATH below (your trained ginger.onnx)
    #   - whisper:   WHISPER_MODEL_PATH below (currently
    #                /root/models/ggml-base.en-q5_1.bin — you also have
    #                ggml-tiny.en-q5_1.bin there if you want to try the
    #                smaller/faster model instead).

Usage
-----
    python3 voice_control.py --threads 4

    # If `--list-audio-devices` doesn't show your mic as expected, or the
    # stream fails to open, try overriding the ALSA device string. This is
    # the only hardware setting meant to be passed on the command line —
    # everything else (including the wake word and whisper model paths) is
    # set in the Config defaults / WAKEWORD_MODEL_PATH / WHISPER_MODEL_PATH
    # below, since none of that changes between runs on this robot.
    python3 voice_control.py --mic-device plughw:APE,0

    # If short commands are taking multiple seconds to transcribe, shrink
    # the whisper encoder context (see design note #9 above) — this is
    # usually the biggest single latency win for short commands:
    python3 voice_control.py --audio-ctx 512

    # To bias recognition toward your fixed command vocabulary (helps
    # accuracy on short/ambiguous words without needing a bigger model):
    python3 voice_control.py \
        --initial-prompt "sit, stand, stop, come here, turn left, turn right, walk forward, walk backward, patrol"

    # To sanity-check what whisper is actually hearing (e.g. if accuracy
    # seems off and you're not sure whether it's the model or the audio
    # capture/resampling), dump each captured command to a wav file:
    python3 voice_control.py --debug-wav-dir /tmp/vc_debug

Tune --threads to (total_cores - cores_reserved_for_ROS2/YOLO). On an
Orin Nano's 6-core Cortex-A78AE, 3-4 threads for whisper is a reasonable
starting point; profile with `tegrastats` and adjust.
"""

from __future__ import annotations

import argparse
import logging
import os
import queue
import re
import sys
import time
import wave
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional, Union

import numpy as np
import sounddevice as sd
import webrtcvad
from scipy import signal
from openwakeword.model import Model as WakeWordModel

try:
    from pywhispercpp.model import Model as WhisperModel
except ImportError:  # pragma: no cover - only hit on machines without it
    WhisperModel = None  # allows --list-audio-devices etc. without whisper installed


LOG = logging.getLogger("voice_control")


# --------------------------------------------------------------------------- #
# Wake word model path — set once here, not on the command line, since this
# doesn't change between runs on this robot. openWakeWord needs the FULL
# path to a custom-trained model file (bare names like "hey_jarvis" only
# resolve for its bundled demo models, not for models you trained yourself
# with the training notebook — passing a bare "ginger" here would silently
# fail to load your model). Point this at either the .onnx or the .tflite
# file produced by training; the .onnx one is used by default below.
# --------------------------------------------------------------------------- #
WAKEWORD_MODEL_PATH = "./ginger.onnx"
# Must be loaded with the matching backend — the detector below explicitly
# requests inference_framework="onnx" to match this .onnx file. If you
# switch this to the .tflite file instead, also change "onnx" to "tflite"
# in WakeWordDetector.__init__ below (openWakeWord does not auto-detect
# this from the file extension and will raise a ValueError if they mismatch).

# Whisper model path — also set once here rather than on the command line.
# Pointing pywhispercpp at a local ggml file (instead of a bare name like
# "base.en") skips its model-resolution/download step entirely and uses
# the quantized model you already have on disk.
WHISPER_MODEL_PATH = "/root/models/ggml-base.en-q5_1.bin"


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

@dataclass
class Config:
    # --- Target format used by VAD / openWakeWord / whisper (unchanged from
    # what those libraries expect) ---
    sample_rate: int = 16000
    # Base frame: 10 ms @ 16kHz = 160 samples. This is the smallest frame
    # webrtcvad accepts (10/20/30 ms), and 8 of these = 80 ms = 1280
    # samples, which is exactly what openWakeWord wants per predict() call.
    frame_samples: int = 160
    wakeword_frame_multiple: int = 8  # 8 * 160 = 1280 samples = 80ms

    # --- Actual microphone hardware config (INMP441 via Jetson Orin Nano
    # APE I2S2 -> ADMAIF1, confirmed with `arecord -l` / `arecord -D ...`).
    # This is the one thing meant to be overridden from the command line
    # (--mic-device), since it's the piece most likely to change if you
    # swap boards/mics; everything else here is fixed for this robot. ---
    mic_device: Union[str, int] = "hw:APE,0"
    mic_native_rate: int = 48000     # only rate this device reliably captures at
    mic_native_channels: int = 2     # interleaved stereo capture (mic is physically mono)
    mic_native_dtype: str = "int32"  # S32_LE
    mic_channel: str = "avg"         # "left" | "right" | "avg" -- which channel(s) hold signal

    # Custom-trained wake word model, loaded by full path (see
    # WAKEWORD_MODEL_PATH above — this is the single place to change it).
    wakeword_model_paths: tuple = (WAKEWORD_MODEL_PATH,)
    wakeword_threshold: float = 0.5

    vad_aggressiveness: int = 2  # 0-3, higher = more aggressive filtering of non-speech
    silence_timeout_ms: int = 800       # stop recording after this much continuous silence
    max_command_ms: int = 6000          # hard cap so a stuck/open mic can't record forever
    min_command_ms: int = 250           # ignore silence-based cutoff before this much audio
    no_speech_timeout_ms: int = 1500    # abort if no speech starts within this long after wake

    whisper_model: str = WHISPER_MODEL_PATH
    whisper_threads: int = 4

    # --- Whisper inference tuning (see design note #9 in the module docstring) ---
    # whisper.cpp's encoder cost scales with audio_ctx; the library default
    # (1500) corresponds to a full 30s window. For short spoken commands,
    # shrinking this is the single biggest lever on inference latency.
    # 0 disables the override and lets pywhispercpp/whisper.cpp use its
    # own default.
    whisper_audio_ctx: int = 512
    # Optional text used to bias decoding toward a known vocabulary (your
    # fixed command set). Cheap accuracy win vs. jumping to a bigger model.
    whisper_initial_prompt: str = ""

    audio_queue_maxframes: int = 500  # ~5s of 10ms frames of backlog before we start dropping

    # If set, each captured command clip is written to this directory as a
    # 16kHz mono wav (before being sent to whisper), so you can listen to
    # exactly what whisper received — useful for telling apart "the model
    # is the bottleneck" from "the mic/resample pipeline is the bottleneck".
    debug_wav_dir: Optional[str] = None


class State(Enum):
    LISTENING_FOR_WAKE = auto()
    AWAITING_SPEECH = auto()
    RECORDING_COMMAND = auto()


# --------------------------------------------------------------------------- #
# Audio capture: captures the mic's *native* format (48kHz/stereo/int32),
# resamples to 16kHz mono int16 inside the callback, and feeds a bounded
# queue of 10ms frames — identical shape/format to what the rest of this
# file expects.
# --------------------------------------------------------------------------- #

class AudioStream:
    """Continuously captures the mic at its native hardware format and
    streams out 10ms int16 mono frames at cfg.sample_rate (16kHz).

    The sounddevice callback runs on a dedicated audio thread and must
    never block or do heavy compute. The resample here is a single short
    FIR filter + integer decimation (cheap, O(frame length)), so it's safe
    to do inline. All inference happens on the main thread.
    """

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._q: "queue.Queue[bytes]" = queue.Queue(maxsize=cfg.audio_queue_maxframes)
        self._stream: Optional[sd.RawInputStream] = None
        self._dropped_frames = 0

        if cfg.mic_native_rate % cfg.sample_rate != 0:
            raise ValueError(
                f"mic_native_rate ({cfg.mic_native_rate}) must be an integer "
                f"multiple of sample_rate ({cfg.sample_rate}) for this simple "
                f"decimating resampler."
            )
        self._decim = cfg.mic_native_rate // cfg.sample_rate  # e.g. 48000/16000 = 3

        # One native-rate callback block == exactly one 10ms output frame.
        self._native_block = self.cfg.frame_samples * self._decim  # e.g. 160*3 = 480

        # Short anti-alias low-pass filter (cutoff just under the *target*
        # Nyquist), designed at the *native* sample rate. Filter state
        # (self._filt_zi) is carried across callbacks so the resampling is
        # continuous rather than re-zeroed every 10ms.
        nyq_target = cfg.sample_rate / 2.0
        cutoff_hz = 0.9 * nyq_target
        self._filt_b = signal.firwin(63, cutoff_hz, fs=cfg.mic_native_rate)
        self._filt_zi = signal.lfilter_zi(self._filt_b, [1.0]) * 0.0

    def _callback(self, indata, frames, time_info, status):
        if status:
            # e.g. input overflow — log but never raise/block in the audio thread
            LOG.debug("sounddevice status: %s", status)

        try:
            native = np.frombuffer(bytes(indata), dtype=np.int32).reshape(
                -1, self.cfg.mic_native_channels
            )
        except ValueError:
            LOG.warning("Unexpected audio buffer size in callback, dropping frame")
            return

        if self.cfg.mic_channel == "left":
            mono_i32 = native[:, 0]
        elif self.cfg.mic_channel == "right":
            mono_i32 = native[:, 1]
        else:  # "avg"
            mono_i32 = native.mean(axis=1)

        # int32 full-scale -> float32 in [-1, 1)
        mono_f32 = mono_i32.astype(np.float32) / 2147483648.0

        filtered, self._filt_zi = signal.lfilter(
            self._filt_b, [1.0], mono_f32, zi=self._filt_zi
        )
        decimated = filtered[:: self._decim]  # e.g. 480 samples @48kHz -> 160 @16kHz

        pcm16 = np.clip(decimated * 32767.0, -32768, 32767).astype(np.int16)
        frame_bytes = pcm16.tobytes()

        try:
            self._q.put_nowait(frame_bytes)
        except queue.Full:
            # Consumer is behind. Drop the oldest frame to keep latency
            # bounded rather than letting the backlog grow unboundedly.
            try:
                self._q.get_nowait()
                self._q.put_nowait(frame_bytes)
            except queue.Empty:
                pass
            self._dropped_frames += 1

    def start(self):
        try:
            self._stream = sd.RawInputStream(
                samplerate=self.cfg.mic_native_rate,
                blocksize=self._native_block,
                device=self.cfg.mic_device,
                dtype=self.cfg.mic_native_dtype,
                channels=self.cfg.mic_native_channels,
                callback=self._callback,
            )
            self._stream.start()
        except Exception:
            LOG.error(
                "Failed to open mic device %r at %dHz/%dch/%s. "
                "Run with --list-audio-devices to see what PortAudio sees, "
                "and try --mic-device plughw:APE,0 as a fallback.",
                self.cfg.mic_device,
                self.cfg.mic_native_rate,
                self.cfg.mic_native_channels,
                self.cfg.mic_native_dtype,
            )
            raise

        LOG.info(
            "Audio stream started: device=%s native=%dHz/%dch/%s (channel=%s) "
            "-> resampled to %dHz mono int16, 10ms frames",
            self.cfg.mic_device,
            self.cfg.mic_native_rate,
            self.cfg.mic_native_channels,
            self.cfg.mic_native_dtype,
            self.cfg.mic_channel,
            self.cfg.sample_rate,
        )

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def read_frame(self, timeout: float = 1.0) -> Optional[bytes]:
        """Blocks (briefly) for the next 10ms int16 mono frame @ cfg.sample_rate."""
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None


# --------------------------------------------------------------------------- #
# Wake word detection
# --------------------------------------------------------------------------- #

class WakeWordDetector:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        names = list(cfg.wakeword_model_paths)

        # Fail fast with a clear message if the custom model file isn't
        # actually there, instead of letting openWakeWord's constructor
        # raise a confusing low-level error deeper in the stack.
        for path in names:
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Wake word model not found at {path!r}. Copy your "
                    f"trained .onnx/.tflite file to that path, or update "
                    f"WAKEWORD_MODEL_PATH near the top of this file."
                )

        # openWakeWord's Model() constructor resolves bundled short names
        # ("hey_jarvis", etc.) or explicit .onnx paths internally. The
        # exact keyword argument name has changed across openwakeword
        # releases (wakeword_models vs. the older wakeword_model_paths), so
        # try both rather than depending on a specific installed version.
        self.model = None
        last_err: Optional[Exception] = None
        for kwargs in (
            {"wakeword_models": names, "inference_framework": "onnx"},
            {"wakeword_model_paths": names, "inference_framework": "onnx"},
        ):
            try:
                self.model = WakeWordModel(**kwargs)
                break
            except TypeError as e:
                last_err = e
                continue
        if self.model is None:
            raise RuntimeError(
                f"Could not construct openwakeword Model() with wake word "
                f"paths {names!r} — the installed openwakeword version may "
                f"use a different constructor signature. Original error: {last_err}"
            )

        self._buf = bytearray()
        self._chunk_bytes = cfg.frame_samples * cfg.wakeword_frame_multiple * 2  # int16 -> 2 bytes/sample

    def feed(self, frame: bytes) -> Optional[str]:
        """Feed one 10ms int16 frame. Returns the triggered wakeword name,
        or None. Internally batches frames into the 80ms chunks openWakeWord
        expects, to minimize per-call overhead."""
        self._buf.extend(frame)
        if len(self._buf) < self._chunk_bytes:
            return None

        chunk = bytes(self._buf[: self._chunk_bytes])
        del self._buf[: self._chunk_bytes]

        audio = np.frombuffer(chunk, dtype=np.int16)
        predictions = self.model.predict(audio)
        for name, score in predictions.items():
            if score >= self.cfg.wakeword_threshold:
                return name
        return None

    def reset(self):
        """Clear internal streaming buffers after a detection so stale
        activation state can't cause an immediate re-trigger."""
        self._buf.clear()
        self.model.reset()


# --------------------------------------------------------------------------- #
# VAD-gated command recorder
# --------------------------------------------------------------------------- #

class CommandRecorder:
    """After a wake word fires, records audio until the user stops talking
    (VAD-based silence detection), a hard time cap is hit, or the user
    never speaks at all (no-speech timeout)."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.vad = webrtcvad.Vad(cfg.vad_aggressiveness)
        self.frame_ms = int(1000 * cfg.frame_samples / cfg.sample_rate)  # 10ms

    def record(self, stream: AudioStream) -> Optional[np.ndarray]:
        frames: list[bytes] = []
        silence_ms = 0
        voiced_ms = 0
        elapsed_ms = 0
        speech_started = False

        while True:
            frame = stream.read_frame(timeout=0.5)
            if frame is None:
                # No audio arriving at all — treat like silence, but don't spin forever.
                elapsed_ms += self.frame_ms
                if elapsed_ms >= self.cfg.max_command_ms:
                    break
                continue

            elapsed_ms += self.frame_ms
            is_speech = self.vad.is_speech(frame, self.cfg.sample_rate)

            if is_speech:
                speech_started = True
                voiced_ms += self.frame_ms
                silence_ms = 0
            else:
                silence_ms += self.frame_ms

            frames.append(frame)

            if not speech_started and elapsed_ms >= self.cfg.no_speech_timeout_ms:
                LOG.info("No speech detected after wake word, aborting.")
                return None

            if (
                speech_started
                and voiced_ms >= 1  # at least some voiced audio captured
                and elapsed_ms >= self.cfg.min_command_ms
                and silence_ms >= self.cfg.silence_timeout_ms
            ):
                break

            if elapsed_ms >= self.cfg.max_command_ms:
                LOG.info("Max command duration reached, cutting off.")
                break

        if not speech_started:
            return None

        raw = b"".join(frames)
        pcm16 = np.frombuffer(raw, dtype=np.int16)
        # whisper.cpp expects float32 mono samples normalized to [-1, 1]
        audio_f32 = pcm16.astype(np.float32) / 32768.0
        return audio_f32


# --------------------------------------------------------------------------- #
# Transcription (whisper.cpp via pywhispercpp, model loaded once)
# --------------------------------------------------------------------------- #

class Transcriber:
    def __init__(self, cfg: Config):
        if WhisperModel is None:
            raise RuntimeError(
                "pywhispercpp is not installed. Install with: "
                "GGML_CUDA=0 pip install pywhispercpp"
            )
        self.cfg = cfg

        # Fail fast with a clear message if the local ggml file isn't
        # actually at the hardcoded path, rather than a confusing error
        # from deep inside pywhispercpp's model loading.
        if os.sep in cfg.whisper_model or cfg.whisper_model.endswith(".bin"):
            if not os.path.exists(cfg.whisper_model):
                raise FileNotFoundError(
                    f"Whisper model not found at {cfg.whisper_model!r}. "
                    f"Update WHISPER_MODEL_PATH near the top of this file, "
                    f"or copy the ggml file to that path."
                )

        init_kwargs = dict(
            n_threads=cfg.whisper_threads,
            print_progress=False,
            print_realtime=False,
            single_segment=True,   # short commands -> one segment, less overhead
            no_context=True,       # don't carry context between unrelated commands
        )
        # NOTE: earlier versions of this script passed context_params={"use_gpu": False}
        # here. pywhispercpp's Model() constructor doesn't actually accept a
        # context_params kwarg — passing it raises a TypeError at startup.
        # CPU-only inference is instead guaranteed at build time by
        # installing with GGML_CUDA=0 (see the module docstring's Install
        # section), so nothing extra needs to be passed here.
        if cfg.whisper_initial_prompt:
            init_kwargs["initial_prompt"] = cfg.whisper_initial_prompt

        self.model = WhisperModel(cfg.whisper_model, **init_kwargs)

        # Whether this pywhispercpp build accepts n_threads/audio_ctx again
        # at transcribe() time is version-dependent. We detect once here
        # (rather than try/except on every single command) so the hot path
        # stays cheap.
        import inspect
        self._transcribe_sig_params = set(
            inspect.signature(self.model.transcribe).parameters.keys()
        )

        self._debug_wav_idx = 0
        if cfg.debug_wav_dir:
            os.makedirs(cfg.debug_wav_dir, exist_ok=True)

    def _maybe_dump_debug_wav(self, audio_f32: np.ndarray) -> None:
        if not self.cfg.debug_wav_dir:
            return
        self._debug_wav_idx += 1
        path = os.path.join(
            self.cfg.debug_wav_dir, f"command_{self._debug_wav_idx:04d}.wav"
        )
        pcm16 = np.clip(audio_f32 * 32768.0, -32768, 32767).astype(np.int16)
        try:
            with wave.open(path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # int16
                wf.setframerate(self.cfg.sample_rate)
                wf.writeframes(pcm16.tobytes())
            LOG.debug("Wrote debug wav: %s", path)
        except Exception:
            LOG.exception("Failed to write debug wav to %s", path)

    def transcribe(self, audio_f32: np.ndarray) -> str:
        self._maybe_dump_debug_wav(audio_f32)

        # Pass n_threads / audio_ctx again at transcribe() time when the
        # installed pywhispercpp version supports it there — some versions
        # only honor n_threads from __init__, others expect (or additionally
        # accept) it per-call. audio_ctx in particular is usually only
        # exposed per-call. See design note #9 at the top of this file:
        # shrinking audio_ctx from whisper.cpp's 1500 (~30s) default is the
        # single biggest lever on latency for short commands.
        call_kwargs = {}
        if "n_threads" in self._transcribe_sig_params:
            call_kwargs["n_threads"] = self.cfg.whisper_threads
        if self.cfg.whisper_audio_ctx and "audio_ctx" in self._transcribe_sig_params:
            call_kwargs["audio_ctx"] = self.cfg.whisper_audio_ctx

        segments = self.model.transcribe(audio_f32, **call_kwargs)
        return " ".join(seg.text.strip() for seg in segments).strip()


# --------------------------------------------------------------------------- #
# Intent parsing / dispatch — replace with your existing ReAct fallback
# heuristic / ROS2 publisher.
# --------------------------------------------------------------------------- #

COMMAND_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bsit\b", re.I), "sit"),
    (re.compile(r"\b(stand|get up)\b", re.I), "stand"),
    (re.compile(r"\b(come here|come)\b", re.I), "come_here"),
    (re.compile(r"\b(stop|halt|freeze)\b", re.I), "stop"),
    (re.compile(r"\bturn left\b", re.I), "turn_left"),
    (re.compile(r"\bturn right\b", re.I), "turn_right"),
    (re.compile(r"\b(walk forward|move forward|forward)\b", re.I), "walk_forward"),
    (re.compile(r"\b(walk back|move back|backward|back up)\b", re.I), "walk_backward"),
    (re.compile(r"\bpatrol\b", re.I), "patrol"),
]


def parse_intent(text: str) -> Optional[str]:
    """Fast keyword-based matching for time-critical, fixed commands.
    Anything that doesn't match falls through to None so the caller can
    route it to your slower LLM/ReAct path for compound/free-form instructions.
    """
    for pattern, action in COMMAND_PATTERNS:
        if pattern.search(text):
            return action
    return None


def dispatch_command(action: Optional[str], raw_text: str) -> None:
    """Hook point: wire this into your ROS2 publisher / ReAct agent loop.

    Example (ROS2, rclpy):
        self.cmd_pub.publish(String(data=action))

    For anything parse_intent() couldn't match (action is None), forward
    raw_text into your existing ReAct-style LLM agent loop as a fallback,
    same as your home-robot assignment does.
    """
    if action is not None:
        LOG.info("DISPATCH fast-path action=%s  (raw_text=%r)", action, raw_text)
    else:
        LOG.info("DISPATCH fallback -> ReAct agent  (raw_text=%r)", raw_text)


# --------------------------------------------------------------------------- #
# Main state machine
# --------------------------------------------------------------------------- #

_SPINNER = "|/-\\"


class VoiceController:
    def __init__(self, cfg: Config, on_command: Callable[[Optional[str], str], None] = dispatch_command):
        self.cfg = cfg
        self.stream = AudioStream(cfg)
        self.wakeword = WakeWordDetector(cfg)
        self.recorder = CommandRecorder(cfg)
        self.transcriber = Transcriber(cfg)
        self.on_command = on_command
        self._running = False

    def _print_banner(self):
        print("\n" + "=" * 60)
        print(" Voice control ready")
        print(f"   mic:        {self.cfg.mic_device} "
              f"({self.cfg.mic_native_rate}Hz/{self.cfg.mic_native_channels}ch/"
              f"{self.cfg.mic_native_dtype} -> {self.cfg.sample_rate}Hz mono)")
        print(f"   wake word:  {self.cfg.wakeword_model_paths} "
              f"(threshold={self.cfg.wakeword_threshold})")
        print(f"   whisper:    {self.cfg.whisper_model} ({self.cfg.whisper_threads} threads, "
              f"audio_ctx={self.cfg.whisper_audio_ctx or 'default'})")
        if self.cfg.whisper_initial_prompt:
            print(f"   prompt:     {self.cfg.whisper_initial_prompt!r}")
        if self.cfg.debug_wav_dir:
            print(f"   debug wav:  {self.cfg.debug_wav_dir}")
        print("=" * 60 + "\n")

    def run(self):
        self.stream.start()
        self._running = True
        state = State.LISTENING_FOR_WAKE
        self._print_banner()
        LOG.info("Ready. Listening for wake word...")

        spin_idx = 0
        last_heartbeat = 0.0

        try:
            while self._running:
                if state == State.LISTENING_FOR_WAKE:
                    # Live "waiting for wake word" prompt, updated in place
                    # so it doesn't spam the log/terminal with a new line
                    # every 10ms.
                    now = time.time()
                    if now - last_heartbeat > 0.15:
                        sys.stdout.write(
                            f"\r  {_SPINNER[spin_idx % len(_SPINNER)]} "
                            f"listening for wake word ('{self.cfg.wakeword_model_paths[0]}')... "
                        )
                        sys.stdout.flush()
                        spin_idx += 1
                        last_heartbeat = now

                    frame = self.stream.read_frame(timeout=1.0)
                    if frame is None:
                        continue
                    triggered = self.wakeword.feed(frame)
                    if triggered:
                        sys.stdout.write("\r" + " " * 70 + "\r")  # clear the spinner line
                        print(f"  ✔ wake word detected: {triggered}")
                        LOG.info("Wake word detected: %s", triggered)
                        self.wakeword.reset()
                        state = State.RECORDING_COMMAND

                elif state == State.RECORDING_COMMAND:
                    print("  🎙️  listening for your command...")
                    t0 = time.time()
                    audio = self.recorder.record(self.stream)
                    LOG.debug("Recording phase took %.2fs", time.time() - t0)

                    if audio is None:
                        print("  (no speech captured — back to listening)\n")
                        state = State.LISTENING_FOR_WAKE
                        continue

                    t0 = time.time()
                    text = self.transcriber.transcribe(audio)
                    dt = time.time() - t0
                    LOG.debug("Transcription took %.2fs -> %r", dt, text)
                    print(f"  (transcription took {dt:.2f}s)")

                    if text:
                        print(f"  heard: {text!r}")
                        action = parse_intent(text)
                        self.on_command(action, text)
                    else:
                        print("  (empty transcription, ignoring)")
                    print()

                    state = State.LISTENING_FOR_WAKE

        except KeyboardInterrupt:
            print("\nInterrupted, shutting down.")
            LOG.info("Interrupted, shutting down.")
        finally:
            self.stop()

    def stop(self):
        self._running = False
        self.stream.stop()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # NOTE: the whisper model path is intentionally NOT a CLI flag either —
    # it's hardcoded via WHISPER_MODEL_PATH near the top of this file
    # (currently pointing at ggml-base.en-q5_1.bin), for the same reason as
    # the wake word model path: it doesn't change between runs on this robot.
    # Swap in ggml-tiny.en-q5_1.bin there instead if you want faster/lighter
    # at the cost of some accuracy.
    p.add_argument("--threads", type=int, default=4, help="whisper.cpp inference threads")
    p.add_argument("--audio-ctx", type=int, default=512,
                    help="whisper.cpp encoder context size. Default whisper.cpp behavior "
                         "processes a full ~30s window (audio_ctx=1500) no matter how short "
                         "your clip is -- this is usually why short commands take multiple "
                         "seconds. Shrinking this (e.g. 256-512 for 1-2s commands) is the "
                         "single biggest lever on latency. Set to 0 to leave whisper.cpp's "
                         "own default in place.")
    p.add_argument("--initial-prompt", default="",
                    help="Text used to bias whisper's decoding toward a known vocabulary "
                         "(e.g. your fixed robot command set). Cheap accuracy win that "
                         "doesn't cost any extra latency. Example: "
                         "'sit, stand, stop, come here, turn left, turn right, walk forward, "
                         "walk backward, patrol'")
    p.add_argument("--debug-wav-dir", default=None,
                    help="If set, write each captured command clip to this directory as a "
                         "16kHz mono wav BEFORE it's sent to whisper, so you can listen to "
                         "exactly what whisper receives. Useful for telling apart a mic/"
                         "resampling problem from a model-accuracy problem.")
    # NOTE: the wake word model path is intentionally NOT a CLI flag — it's
    # hardcoded via WAKEWORD_MODEL_PATH near the top of this file, since it
    # doesn't change between runs on this robot. Only --wakeword-threshold
    # remains here since you may want to tune it without editing the file.
    p.add_argument("--wakeword-threshold", type=float, default=0.5)
    p.add_argument("--vad-aggressiveness", type=int, default=2, choices=[0, 1, 2, 3])
    p.add_argument("--silence-timeout-ms", type=int, default=800)
    p.add_argument("--max-command-ms", type=int, default=6000)

    # --- mic hardware options (the one thing meant to be overridden here) ---
    p.add_argument("--mic-device", default="hw:APE,0",
                    help="ALSA/PortAudio input device string or index for the mic "
                         "(default: hw:APE,0 — confirmed via `arecord -l` on Jetson Orin "
                         "Nano + INMP441). Try 'plughw:APE,0' if the raw hw: device "
                         "fails to open.")
    p.add_argument("--mic-native-rate", type=int, default=48000,
                    help="Native sample rate the mic device captures at (default: 48000, "
                         "confirmed the only rate hw:APE,0 reliably supports).")
    p.add_argument("--mic-native-channels", type=int, default=2,
                    help="Native channel count the mic device captures (default: 2, "
                         "since hw:APE,0 only opens in stereo even for a mono mic).")
    p.add_argument("--mic-channel", default="avg", choices=["left", "right", "avg"],
                    help="Which native channel(s) carry the real mic signal (default: avg "
                         "of both channels; try 'left' or 'right' if averaging sounds off).")

    p.add_argument("--list-audio-devices", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv=None):
    args = build_arg_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.list_audio_devices:
        print(sd.query_devices())
        return 0

    # sounddevice/PortAudio treats an int device arg as an index and a str
    # arg as a name-substring match. --list-audio-devices prints numeric
    # indices (e.g. "4  NVIDIA Jetson Orin Nano APE: - (hw:1,0)"), so if the
    # user passed a plain number, convert it to int so it selects by index
    # rather than being (mis)treated as a literal device name.
    mic_device: Union[str, int] = args.mic_device
    if isinstance(mic_device, str) and mic_device.strip().lstrip("-").isdigit():
        mic_device = int(mic_device.strip())

    cfg = Config(
        # whisper_model intentionally left as the Config default
        # (WHISPER_MODEL_PATH) — not settable from the CLI.
        whisper_threads=args.threads,
        whisper_audio_ctx=args.audio_ctx,
        whisper_initial_prompt=args.initial_prompt,
        # wakeword_model_paths intentionally left as the Config default
        # (WAKEWORD_MODEL_PATH) — not settable from the CLI.
        wakeword_threshold=args.wakeword_threshold,
        vad_aggressiveness=args.vad_aggressiveness,
        silence_timeout_ms=args.silence_timeout_ms,
        max_command_ms=args.max_command_ms,
        mic_device=mic_device,
        mic_native_rate=args.mic_native_rate,
        mic_native_channels=args.mic_native_channels,
        mic_channel=args.mic_channel,
        debug_wav_dir=args.debug_wav_dir,
    )

    controller = VoiceController(cfg)
    controller.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
