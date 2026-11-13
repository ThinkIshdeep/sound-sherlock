# Synopsis — Sound Sherlock

**Ishdeep Singh · 12 November 2026**

## V2 interface release

An audio inspection workstation.

- Actual WAV playback with a synchronized waveform/spectrogram cursor
- A/B recording slots backed by distinct immutable WAV files
- Drag a time region, seek and loop the selection
- Spectral bands, detector score, quality checks and real WAV import

A/B slots are session UI state. Generated WAV files persist in runtime/media; no real-machine fault labels are inferred. The underlying domain scope and research-extension boundaries below remain explicit.

## Implemented release

Runnable source: `lab/audio.py`. Interface and backend are included. Tests and benchmark outputs accompany this distribution.

## Limits of the implemented release

Synthetic audio reference, spectral baseline and Isolation Forest. No real-device fault diagnosis or DCASE benchmark.

## Measured evaluation

```json
{
  "detector": "spectral_energy_baseline",
  "auroc": 1.0,
  "average_precision": 0.9999999999999998,
  "false_positive_rate": 0.3111111111111111,
  "recall": 1.0,
  "isolation_forest": {
    "auroc": 0.7135802469135802,
    "false_positive_rate": 0.03333333333333333,
    "recall": 0.06666666666666667
  },
  "test_recordings": 180,
  "threshold": 0.0275065585965067,
  "note": "Synthetic held-out recordings with changed noise. The default spectral baseline is compared with Isolation Forest, not hidden behind it. No real-device validation is bundled."
}
```

## Original specification and proposed extensions

The material below preserves the design ambitions. Future-tense features and anticipated challenges are not completed-development claims.

Sound Sherlock

**Tagline:** The fan sounds normal. The spectrogram would like to disagree.

### Concept, problem, and users

Sound Sherlock analyzes recordings of machine operation and highlights unusual patterns. A change in sound may be useful for condition monitoring, but the recording also contains the room, microphone, operating speed, and background noise. The model must avoid learning those shortcuts.

Target users are audio-ML learners, maintenance researchers, and makers monitoring safely operated devices. The key question is whether a representation generalizes to unfamiliar devices and recording conditions while maintaining an acceptable false-alarm rate.

### Proposed product and workflow

Users record or upload audio, confirm the device and operating context, and inspect a waveform, spectrogram, anomaly score, and comparable examples. Where trustworthy fault labels exist, a separate classifier may propose a fault category. Otherwise, the output is an unusual-condition flag with uncertainty.

Screens: recording/upload, audio quality checks, spectrogram, comparison library, device trend, and evaluation report. The app should distinguish recording-quality failure from a machine anomaly. Supported file types, maximum duration, channel handling, and expected sample rate must be documented in the implemented release.

### Data and system design

Records: `Device`, `RecordingSession`, `AudioClip`, `OperatingCondition`, `FeatureVersion`, `AnomalyScore`, and `ReviewLabel`. Preserve device IDs, microphone IDs, room/session IDs, sampling rate, and preprocessing settings.

DCASE's machine-condition monitoring tasks provide a candidate benchmark starting point [R5]. Choose one exact dataset release, follow its access terms and task protocol, and retain its machine/domain grouping. For self-recorded data, collect ordinary operation across rooms, microphones, speeds, and days. Do not create dangerous physical faults for a demonstration.

### Algorithms and experiments

Baseline: simple spectral features with a distance-based normality score. Next: log-mel spectrograms with an autoencoder or learned audio representation. Compare normalized embedding distance, a one-class method, and a labelled classifier only where labels justify it.

Training-only normalization statistics must be frozen for evaluation. Threshold selection uses validation data, not the final test set. A highlighted spectrogram region identifies where the model reacts; it does not establish a physical cause. Unknown-condition handling is preferable to forcing every recording into a familiar fault label.

Metrics: AUROC, precision–recall performance, false-alarm rate at a declared threshold, and recall at a fixed false-alarm budget. Report per-device and per-domain results, not only an aggregate. Keep all windows from one recording session in the same partition. Ablate augmentation and domain normalization; test added noise and unseen microphones.

### Anticipated problems, in my voice

| What could go wrong | My likely reaction | Engineering response |
|---|---|---|
| The model identifies the recording room | “Excellent bedroom classifier. Slightly less excellent mechanic.” | Device/session/domain-separated evaluation |
| Silence or clipping looks like a fault | “The motor is innocent. The microphone needs supervision.” | Audio quality checks before model inference |
| One device always sounds unusual | “It has confused personality with damage.” | Context-aware normal references and per-domain reporting |

### Demo, milestones, and limits

Compare a normal recording, a permitted labelled anomalous clip, and the same normal recording under background noise. Show when the model abstains. Milestones: audio pipeline; reference baseline; domain-split evaluation; representation model; trend UI. Deliver reproducible audio benchmarks and reviewable alerts. This is a monitoring aid, not a verified repair diagnosis or a replacement for inspection.




## Problems actually encountered during the makeover

| The problem | In my voice | What changed |
|---|---|---|
| Sample B overwrote the file used by sample A | “Bro, this is an A/B test, why did B steal A’s identity?” | Recordings now get unique file names; a regression test checks both files remain distinct and unchanged. |
| A duplicate highlight followed row positions instead of duplicate evidence | “Apparently every third row had been arrested on vibes.” | Duplicate highlights now use exact record content and jump to a real duplicate. |
| The table displayed a rounded number that search did not match | “I copied the number from your own screen, my guy.” | Search checks both raw values and the formatted values visible in the table. |
| Graph labels became tiny on a phone | “Causal inference, now available to ants.” | Graph workspaces keep readable node widths and scroll within their own viewport. |
| Robot movement and the play button disagreed about whether it was running | “Gordon left the parking spot while the button was still contemplating life.” | The live flag is synchronized after accepted commands and remains off after rejected commands. |
| Fast screenshots caught an interface between renders | “The UI took a smoke break precisely when the camera arrived.” | Captures were inspected, incomplete frames replaced, and videos labelled as edited screenshots. |

These are observed build issues. Proposed research challenges in the original specifications remain proposed; this log does not invent months of model training or real deployments.
