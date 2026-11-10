import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT.parent/'central/docs/target'  # integration test path when working across provided snapshots
spec=importlib.util.spec_from_file_location('sync_koa_target',ROOT/'scripts/sync_koa_target.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class TargetMirrorTests(unittest.TestCase):
    def test_committed_bundle_integrity(self):
        self.assertEqual(module.verify_bundle(ROOT/'docs/final-system'),[])

    def test_24_chain_pages(self):
        m=json.loads((ROOT/'docs/final-system/_MANIFEST.json').read_text(encoding='utf8'))
        self.assertEqual(sum(x['destination'].startswith('functional-chains/chains/FC-') for x in m['pages']),24)
        self.assertEqual(m['status'],'DERIVED_TARGET_DESIGN_NOT_DEPLOYMENT')

    def test_local_source_generator_and_link_rewrite(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'repo/docs/target'
            src.mkdir(parents=True)
            (src/'functional-chains/chains').mkdir(parents=True)
            (src/'functional-chains/README.md').write_text('# Index\n[First](chains/FC-01-example.md)\n')
            for i in range(1,25):
                (src/f'functional-chains/chains/FC-{i:02}-example.md').write_text(f'# FC-{i:02} — example\n')
            (src/'README.md').write_text('# Start\n[Chains](functional-chains/README.md)\n')
            result=module.generate(src,'test-ref')
            self.assertIn(b'(functional-chains/index.md)',result['index.md'])
            self.assertIn(b'(chains/FC-01-example.md)',result['functional-chains/index.md'])
            self.assertEqual(len([x for x in result if x.startswith('functional-chains/chains/')]),24)

if __name__=='__main__':unittest.main()
