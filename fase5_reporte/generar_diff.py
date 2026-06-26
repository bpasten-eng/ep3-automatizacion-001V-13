#!/usr/bin/env python3
import json, os

baseline_dir = '../fase1_baseline/evidencias/baseline_001V-13'
snapshot_dir = 'evidencias/snapshot_final_001V-13'
diff_dir     = 'evidencias/diff_001V-13'
os.makedirs(diff_dir, exist_ok=True)

features = ['interface', 'platform', 'routing']

for feature in features:
    baseline_file = f'{baseline_dir}/{feature}_iosxe_CSR1kv_ops.txt'
    snapshot_file = f'{snapshot_dir}/{feature}_iosxe_CSR1kv_ops.txt'
    diff_file     = f'{diff_dir}/diff_{feature}.txt'

    try:
        with open(baseline_file) as f:
            baseline_text = f.read()
        with open(snapshot_file) as f:
            snapshot_text = f.read()

        baseline_lines = set(baseline_text.splitlines())
        snapshot_lines = set(snapshot_text.splitlines())

        added   = snapshot_lines - baseline_lines
        removed = baseline_lines - snapshot_lines

        with open(diff_file, 'w') as f:
            f.write(f"=== DIFF {feature.upper()} ===\n")
            f.write(f"Baseline : {baseline_file}\n")
            f.write(f"Snapshot : {snapshot_file}\n\n")
            f.write(f"--- Lineas removidas ({len(removed)}) ---\n")
            for line in sorted(removed)[:50]:
                f.write(f"- {line}\n")
            f.write(f"\n+++ Lineas agregadas ({len(added)}) ---\n")
            for line in sorted(added)[:50]:
                f.write(f"+ {line}\n")

        print(f'[OK] diff {feature}: {len(removed)} removidas, {len(added)} agregadas')

    except Exception as e:
        print(f'[FAIL] {feature}: {e}')

print('Diff completado.')
