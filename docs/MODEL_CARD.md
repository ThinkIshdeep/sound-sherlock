# Model and simulator card — Sound Sherlock

## Intended use

An audio inspection workbench combining spectral analysis, a transparent detector and an Isolation Forest reference experiment.

## Implemented methods

- Sixteen-bit PCM WAV import and bounded resampling
- Silence/clipping checks, waveform and STFT spectrogram
- Log-frequency features with finite-value safeguards
- Validation-threshold spectral detector and Isolation Forest comparison
- Seeded synthetic normal/anomalous recordings and noise shifts

Some projects use deterministic simulators and rules rather than trained neural models. Those distinctions are retained in this card and the source.

## Evaluation

See `docs/EXPERIMENTS.md` and the machine-readable reports. No pretrained foundation-model weights or real-world efficacy certification are included. Parameters, splits and synthetic generators are visible in source.

## Limitations

Synthetic audio reference, spectral baseline and Isolation Forest. No real-device fault diagnosis or DCASE benchmark.

## Extensions not implemented in this release

- Real-machine normal references and device/domain-separated datasets
- Fault-category classification and industrial validation
