"""Download project-local runtimes and the official Movies dataset."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / '.runtime'
RUNTIME.mkdir(exist_ok=True)
(ROOT / 'data').mkdir(exist_ok=True)

def download(url, target):
    target = Path(target)
    if target.exists():
        print('Already downloaded:', target.name, flush=True)
        return target
    print('Downloading:', target.name, flush=True)
    temp = target.with_suffix(target.suffix + '.part')
    with urllib.request.urlopen(url, timeout=120) as response, temp.open('wb') as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)
    temp.replace(target)
    print('Downloaded:', target.name, target.stat().st_size, flush=True)
    return target

def unpack(url, target, folder):
    archive = download(url, target)
    with zipfile.ZipFile(archive) as z:
        z.extractall(folder)
    print('Extracted:', archive.name, flush=True)

if __name__ == '__main__':
    releases = json.load(urllib.request.urlopen('https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=5'))
    asset = next(a for r in releases for a in r['assets'] if a['name'].endswith('bin-win-cpu-x64.zip'))
    jobs = [
        (unpack, ('https://dist.neo4j.org/neo4j-community-2026.09.0-windows.zip', RUNTIME/'neo4j.zip', RUNTIME)),
        (unpack, (asset['browser_download_url'], RUNTIME/'llama.zip', RUNTIME/'llama')),
        (download, ('https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf', RUNTIME/'model-3b.gguf')),
        (download, ('https://raw.githubusercontent.com/neo4j-graph-examples/movies/main/scripts/movies.cypher', ROOT/'data'/'movies.cypher')),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fn, *args) for fn, args in jobs]
        for f in futures:
            f.result()
    manifest = {'neo4j':'2026.09.0','llama_asset':asset['name'],
                'model':'Qwen2.5-3B-Instruct Q4_K_M',
                'dataset':'https://github.com/neo4j-graph-examples/movies',
                'dataset_sha256':hashlib.sha256((ROOT/'data'/'movies.cypher').read_bytes()).hexdigest()}
    (ROOT/'data'/'provenance.json').write_text(json.dumps(manifest,indent=2))
