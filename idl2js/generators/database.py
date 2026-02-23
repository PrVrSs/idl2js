import hashlib
import json
from pathlib import Path


class ExampleDatabase:
    """Persists interesting choice sequences to disk.

    Directory structure:
        base_path/
            <key_hash>/
                <example_hash>.json
    """

    def __init__(self, base_path='.idl2js_db'):
        self._base = Path(base_path)

    def save(self, key, choices, metadata=None):
        key_dir = self._key_dir(key)
        key_dir.mkdir(parents=True, exist_ok=True)

        data = {
            'key': key,
            'choices': [
                [int(c[0]), c[1], c[2], c[3]] for c in choices
            ],
            'metadata': metadata or {},
        }

        example_hash = self._hash_choices(choices)
        path = key_dir / f'{example_hash}.json'

        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, indent=2)

        return path

    def fetch(self, key):
        key_dir = self._key_dir(key)
        if not key_dir.exists():
            return []

        results = []
        for path in sorted(key_dir.glob('*.json')):
            try:
                with open(path, encoding='utf-8') as fp:
                    data = json.load(fp)
                choices = [tuple(c) for c in data['choices']]
                results.append({
                    'choices': choices,
                    'metadata': data.get('metadata', {}),
                    'path': path,
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return sorted(results, key=lambda r: len(r['choices']))

    def delete(self, key, choices):
        key_dir = self._key_dir(key)
        example_hash = self._hash_choices(choices)
        path = key_dir / f'{example_hash}.json'
        if path.exists():
            path.unlink()

        if key_dir.exists() and not any(key_dir.iterdir()):
            key_dir.rmdir()

    def keys(self):
        if not self._base.exists():
            return []
        return [
            d.name for d in self._base.iterdir() if d.is_dir()
        ]

    def clear(self):
        if not self._base.exists():
            return
        for key_dir in self._base.iterdir():
            if key_dir.is_dir():
                for f in key_dir.glob('*.json'):
                    f.unlink()
                key_dir.rmdir()

    def _key_dir(self, key):
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self._base / key_hash

    @staticmethod
    def _hash_choices(choices):
        content = str(choices).encode()
        return hashlib.sha256(content).hexdigest()[:16]
