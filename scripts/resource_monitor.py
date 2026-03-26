import subprocess
import time

try:
    import psutil
except ImportError:
    psutil = None

_last_gpu_check_time = 0
_cached_gpu_data = []
_gpu_cache_ttl = 1.0  # seconds

def _get_gpu_stats() -> list:
    global _last_gpu_check_time, _cached_gpu_data
    
    now = time.time()
    if now - _last_gpu_check_time < _gpu_cache_ttl:
        return _cached_gpu_data
        
    gpu_data = []
    try:
        # Expected output format from nvidia-smi:
        # 0, NVIDIA GeForce RTX 3080, 15, 2048, 10240, 65
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"],
            text=True,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        for line in output.strip().split("\n"):
            if not line.strip(): continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 6:
                try:
                    util = float(parts[2]) if parts[2] != '[Not Supported]' else 0.0
                except ValueError:
                    util = 0.0
                    
                try:
                    gpu_data.append({
                        "index": parts[0],
                        "name": parts[1],
                        "utilization_percent": util,
                        "memory_used_mb": float(parts[3]),
                        "memory_total_mb": float(parts[4]),
                        "temperature_c": float(parts[5])
                    })
                except ValueError:
                    pass
    except Exception:
        # Ignore if nvidia-smi is not found or fails
        pass

    _cached_gpu_data = gpu_data
    _last_gpu_check_time = now
    return gpu_data

def get_system_resources() -> dict:
    if not psutil:
        return {"error": "psutil not installed"}
        
    cpu_percent = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    
    return {
        "cpu_percent": cpu_percent,
        "ram_percent": ram.percent,
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "gpus": _get_gpu_stats()
    }

if __name__ == "__main__":
    import json
    # Warm up CPU measurement
    psutil.cpu_percent(interval=None) if psutil else None
    time.sleep(0.1)
    print(json.dumps(get_system_resources(), indent=2))
