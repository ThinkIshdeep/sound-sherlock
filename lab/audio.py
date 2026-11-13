import io, wave, uuid
import numpy as np
from scipy.signal import stft, resample_poly
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.preprocessing import StandardScaler
from .core import Base, decoded, RUNTIME

class Engine(Base):
    actions = Base.actions | {'sample', 'analyze', 'train'}

    def __init__(self):
        super().__init__()
        self.reset({})
        self.fit()

    def reset(self, p):
        self.state = {'normal_samples': 90, 'last_audio': None, 'history': [], 'last_result': None}

    def signal(self, seed, anomaly=False, domain=0):
        r = np.random.default_rng(seed)
        sr = 8000
        t = np.arange(sr * 2) / sr
        f = r.uniform(110, 150)
        noise = 0.018 + r.uniform(0, 0.025) + domain * 0.005
        y = 0.3 * np.sin(2 * np.pi * f * t) + 0.12 * np.sin(2 * np.pi * 2 * f * t) + r.normal(0, noise, len(t))
        if anomaly:
            y += 0.22 * np.sin(2 * np.pi * r.uniform(850, 1100) * t) * (1 + 0.7 * np.sin(2 * np.pi * 8 * t))
        return (y.astype(float), sr)

    def features(self, y, sr):
        if len(y) < sr // 4:
            raise ValueError('Recording must be at least 0.25 seconds')
        f, t, z = stft(y, sr, nperseg=256, noverlap=128)
        power = np.abs(z) ** 2 + 1e-12
        bands = []
        for a, b in zip(np.geomspace(30, sr / 2, 25)[:-1], np.geomspace(30, sr / 2, 25)[1:]):
            mask = (f >= a) & (f < b)
            if not mask.any():
                mask[np.argmin(abs(f - (a + b) / 2))] = True
            bands.append(float(np.log10(power[mask].mean() + 1e-12)))
        centroid = float(np.sum(f[:, None] * power) / power.sum() / sr)
        rms = float(np.sqrt(np.mean(y * y)))
        cross = float(np.mean(y[:-1] * y[1:] < 0))
        high_ratio = float(power[f > 600].sum() / power.sum())
        return (np.array(bands + [centroid, rms, cross, high_ratio]), f, t, np.log10(power))

    def fit(self):
        X = np.array([self.features(*self.signal(i))[0] for i in range(90)])
        self.scaler = StandardScaler().fit(X)
        self.model = IsolationForest(n_estimators=100, contamination=0.08, random_state=42).fit(self.scaler.transform(X))
        self.ref = X.mean(axis=0)
        val = np.array([self.features(*self.signal(i))[0] for i in range(100, 150)])
        scores = -self.model.score_samples(self.scaler.transform(val))
        self.isolation_threshold = float(np.quantile(scores, 0.95))
        self.threshold = float(np.quantile(val[:, -1], 0.95))

    def train(self, p):
        self.fit()
        return {'normal_training_recordings': 90, 'validation_normal_recordings': 50, 'threshold': self.threshold, 'training_domain': 'Synthetic steady rotating tones; not a real machine model.'}

    def sample(self, p):
        kind = p.get('kind', 'normal')
        y, sr = self.signal(int(p.get('seed', 333)), kind == 'anomaly', 1 if kind == 'noise' else 0)
        return self.process(y, sr, f'synthetic-{kind}')

    def analyze(self, p):
        raw = decoded(p)
        try:
            with wave.open(io.BytesIO(raw)) as f:
                channels = f.getnchannels()
                sr = f.getframerate()
                width = f.getsampwidth()
                frames = f.getnframes()
                if width != 2:
                    raise ValueError('Use a 16-bit PCM WAV file')
                if not 4000 <= sr <= 96000 or frames > sr * 30:
                    raise ValueError('Use a 0.25–30 second WAV, sample rate 4–96 kHz')
                y = np.frombuffer(f.readframes(frames), dtype='<i2').astype(float) / 32768
                if channels > 1:
                    y = y.reshape(-1, channels).mean(axis=1)
        except (wave.Error, EOFError) as e:
            raise ValueError('Unable to read WAV. Convert to 16-bit PCM WAV first.') from e
        if sr != 8000:
            from math import gcd
            g = gcd(sr, 8000)
            y = resample_poly(y, 8000 // g, sr // g)
            sr = 8000
        return self.process(y, sr, str(p.get('name', 'uploaded.wav')))

    def process(self, y, sr, name):
        feat, f, t, z = self.features(y, sr)
        score = float(feat[-1])
        isolation_score = float(-self.model.score_samples(self.scaler.transform([feat]))[0])
        rms = float(np.sqrt(np.mean(y * y)))
        clip = float(np.mean(np.abs(y) > 0.99))
        quality = 'silent' if rms < 0.002 else 'clipped' if clip > 0.01 else 'usable'
        RUNTIME.joinpath('media').mkdir(parents=True, exist_ok=True)
        filename = 'recording-' + uuid.uuid4().hex + '.wav'
        path = RUNTIME / 'media' / filename
        with wave.open(str(path), 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
        out = {'name': name, 'score': score, 'threshold': self.threshold, 'score_method': 'High-frequency energy ratio baseline; validation-selected threshold', 'isolation_forest_score': isolation_score, 'isolation_forest_threshold': self.isolation_threshold, 'unusual': score > self.threshold, 'quality': quality, 'rms': rms, 'clipped_fraction': clip, 'duration': len(y) / sr, 'sample_rate': sr, 'waveform': y[::max(1, len(y) // 500)].tolist(), 'spectrogram': z[::2, ::max(1, z.shape[1] // 100)].tolist(), 'bands': feat[:24].tolist(), 'normal_reference': self.ref[:24].tolist(), 'audio_url': '/media/' + filename, 'note': 'Compared with a synthetic reference model. An unusual real recording does not identify a fault.'}
        self.state['last_audio'] = out
        self.state['history'].append({'name': name, 'score': score, 'quality': quality, 'audio_url': out['audio_url']})
        return out

    def evaluate(self, p):
        X = []
        labels = []
        for i in range(180):
            self.check_cancel()
            y, sr = self.signal(5000 + i, bool(i % 2), domain=1)
            X.append(self.features(y, sr)[0])
            labels.append(i % 2)
        iso = -self.model.score_samples(self.scaler.transform(X))
        scores = np.array(X)[:, -1]
        labels = np.array(labels)
        pred = scores > self.threshold
        ip = iso > self.isolation_threshold
        out = {'detector': 'spectral_energy_baseline', 'auroc': float(roc_auc_score(labels, scores)), 'average_precision': float(average_precision_score(labels, scores)), 'false_positive_rate': float(pred[labels == 0].mean()), 'recall': float(pred[labels == 1].mean()), 'isolation_forest': {'auroc': float(roc_auc_score(labels, iso)), 'false_positive_rate': float(ip[labels == 0].mean()), 'recall': float(ip[labels == 1].mean())}, 'test_recordings': 180, 'threshold': self.threshold, 'note': 'Synthetic held-out recordings with changed noise. The default spectral baseline is compared with Isolation Forest, not hidden behind it. No real-device validation is bundled.'}
        self.state['last_result'] = out
        return out
