#!/usr/bin/env python3
from genie.testbed import load
import os, json

testbed = load('../fase1_baseline/testbed_001V-13.yaml')
device = testbed.devices['CSR1kv']

device.connect(learn_hostname=True)

os.makedirs('evidencias/snapshot_final_001V-13', exist_ok=True)

for feature in ['interface', 'platform', 'routing']:
    try:
        learned = device.learn(feature)
        output_path = f'evidencias/snapshot_final_001V-13/{feature}_iosxe_CSR1kv_ops.txt'
        with open(output_path, 'w') as f:
            json.dump(learned.info, f, indent=2, default=str)
        print(f'[OK] {feature} capturado')
    except Exception as e:
        print(f'[FAIL] {feature}: {e}')

device.disconnect()
print('Snapshot final completado.')
