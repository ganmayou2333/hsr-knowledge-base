"""Local release activation is atomic and leaves older sites recoverable."""
import json
import copy
import os
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from tools.preview_artifact import InvalidPreviewArtifact
from tools.preview_release import GRACE_SECONDS, prune, publish
from tools.preview_release_state import active_site
from tools.preview_review_server import ReviewServer
from tools.test_stage_preview import PR, RUN, WORKFLOW, TRUSTED_RUN

HEAD = 'a' * 40


def fixture(site, title='one', head=HEAD):
    site = Path(site)
    bundle = site / 'previews' / '7'
    bundle.mkdir(parents=True)
    (site / 'index.html').write_text(f'<head></head><h1>{title}</h1>', encoding='ascii')
    manifest = {'version': 1, 'repo': 'owner/repo', 'pr': 7, 'head': head, 'base': 'b' * 40,
                'run': 10, 'run_attempt': 1, 'trusted_run': 11, 'trusted_attempt': 1,
                'files': {'index.html': 'c' * 64}}
    (bundle / 'manifest.json').write_text(json.dumps(manifest), encoding='ascii')
    return [7]


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def publish(self, title='one', valid=True):
        with patch('tools.preview_release.reconcile', side_effect=lambda repo, shell, site: fixture(site, title)), \
                patch('tools.preview_release.verify', return_value=1 if valid else 0):
            return publish('owner/repo', self.root, self.root)

    def test_switches_only_after_validation_and_keeps_previous(self):
        self.assertEqual(self.publish('one'), [7])
        first = active_site(self.root)
        with self.assertRaises(InvalidPreviewArtifact):
            self.publish('bad', valid=False)
        self.assertEqual(active_site(self.root), first)
        self.assertEqual(len(list((self.root / 'sites').iterdir())), 1)
        self.assertFalse((self.root / '.publish-lock').exists())
        self.assertEqual(self.publish('two'), [7])
        second = active_site(self.root)
        self.assertNotEqual(first, second)
        self.assertTrue(first.is_dir())
        self.assertIn('two', (second / 'index.html').read_text(encoding='ascii'))

    def test_only_old_owned_releases_are_pruned(self):
        self.publish()
        current = active_site(self.root)
        sites = self.root / 'sites'
        old, foreign = sites / ('site-' + '1' * 32), sites / ('site-' + '2' * 32)
        for site, repo in [(old, 'owner/repo'), (foreign, 'other/repo')]:
            site.mkdir()
            (site / '.preview-release.json').write_text(json.dumps({'version': 1, 'repo': repo, 'name': site.name}), encoding='ascii')
            timestamp = time.time() - GRACE_SECONDS - 10
            os.utime(site, (timestamp, timestamp))
        prune(self.root, 'owner/repo', {current.name})
        self.assertFalse(old.exists())
        self.assertTrue(foreign.is_dir())
        self.assertTrue(current.is_dir())

    def test_collision_does_not_remove_existing_directory(self):
        sites = self.root / 'sites'; sites.mkdir()
        existing = sites / ('site-' + '1' * 32); existing.mkdir()
        (existing / 'keep').write_text('keep', encoding='ascii')
        with patch('tools.preview_release.secrets.token_hex', return_value='1' * 32), \
                patch('tools.preview_release.reconcile', side_effect=InvalidPreviewArtifact('exists')):
            with self.assertRaises(InvalidPreviewArtifact):
                publish('owner/repo', self.root, self.root)
        self.assertEqual((existing / 'keep').read_text(encoding='ascii'), 'keep')

    def test_service_switches_sites_and_invalidates_review_cache(self):
        self.publish('one')
        head = [HEAD]
        def reader(repo, number):
            return {'pr': number, 'head': head[0], 'approved': True, 'reviews': [], 'captured_at': int(time.time())}
        server = ReviewServer(('127.0.0.1', 0), 'owner/repo', reader=reader, site_root=self.root,
                              validator=lambda repo, number, manifest: True)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            address = f'http://127.0.0.1:{server.server_port}'
            with urllib.request.urlopen(address, timeout=5) as response:
                self.assertIn(b'one', response.read())
            self.assertEqual(server.get_review(7)['head'], HEAD)
            other_head = 'd' * 40
            with patch('tools.preview_release.reconcile', side_effect=lambda repo, shell, site: fixture(site, 'two', other_head)), \
                    patch('tools.preview_release.verify', return_value=1):
                publish('owner/repo', self.root, self.root)
            head[0] = other_head
            with urllib.request.urlopen(address, timeout=5) as response:
                self.assertIn(b'two', response.read())
            self.assertEqual(server.get_review(7)['head'], other_head)
            (self.root / 'current').write_text('../invalid', encoding='ascii')
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(address, timeout=5)
            self.assertEqual(error.exception.code, 503)
            error.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_final_verification_failure_keeps_previous_release(self):
        self.publish('one')
        first = active_site(self.root)
        for error in (InvalidPreviewArtifact('new failed run'), OSError('API unavailable')):
            with self.subTest(error=error), patch('tools.preview_release.reconcile', side_effect=lambda repo, shell, site: fixture(site, 'bad')), \
                    patch('tools.preview_release.verify', side_effect=error), self.assertRaises(type(error)):
                publish('owner/repo', self.root, self.root)
            self.assertEqual(active_site(self.root), first)
            self.assertEqual(len(list((self.root / 'sites').iterdir())), 1)

    def test_unlisted_preview_is_never_activated(self):
        self.publish('one')
        first = active_site(self.root)
        def mismatched(repo, shell, site):
            fixture(site, 'bad')
            return []
        with patch('tools.preview_release.reconcile', side_effect=mismatched), \
                patch('tools.preview_release.verify') as verify, self.assertRaises(InvalidPreviewArtifact):
            publish('owner/repo', self.root, self.root)
        verify.assert_not_called()
        self.assertEqual(active_site(self.root), first)

    def test_real_pre_activation_verifier_rejects_new_failure_and_revoked_approval(self):
        pr, build, trusted = copy.deepcopy(PR), copy.deepcopy(RUN), copy.deepcopy(TRUSTED_RUN)
        pr['head']['repo']['id'] = 2
        build['pull_requests'][0]['head']['repo']['id'] = 2
        trusted['pull_requests'][0]['head']['repo']['id'] = 2
        builds = [build]
        main = {'sha': pr['base']['sha']}
        review = {'head': HEAD, 'approved': True}
        def catalog_api(path):
            if path.endswith('/branches/main'): return {'name': 'main', 'commit': {'sha': main['sha']}}
            if path.endswith('/pulls/7'): return copy.deepcopy(pr)
            if path.endswith('/actions/runs/10'): return copy.deepcopy(build)
            if path.endswith('/actions/runs/11'): return copy.deepcopy(trusted)
            if path.endswith('/actions/workflows/wiki-trusted-data.yml'): return copy.deepcopy(WORKFLOW)
            raise AssertionError(path)
        def verifier_api(path, paginate=False):
            if path.endswith('/pulls/7'): return copy.deepcopy(pr)
            if '/wiki-quality.yml/runs?' in path: return [{'total_count': len(builds), 'workflow_runs': copy.deepcopy(builds)}]
            if '/wiki-trusted-data.yml/runs?' in path: return [{'total_count': 1, 'workflow_runs': [copy.deepcopy(trusted)]}]
            raise AssertionError(path)
        with patch('tools.preview_release.reconcile', side_effect=lambda repo, shell, site: fixture(site)), \
                patch('tools.preview_catalog.gh_api', side_effect=catalog_api), \
                patch('tools.verify_preview_publication.gh_api', side_effect=verifier_api), \
                patch('tools.verify_preview_publication.snapshot', side_effect=lambda *args: copy.deepcopy(review)):
            self.assertEqual(publish('owner/repo', self.root, self.root), [7])
            first = active_site(self.root)
            # Pull API stays stale while the live main moves, as observed on
            # real fork PR #48. Activation must leave the old pointer intact.
            main['sha'] = 'c' * 40
            with self.assertRaises(InvalidPreviewArtifact): publish('owner/repo', self.root, self.root)
            self.assertEqual(active_site(self.root), first)
            main['sha'] = pr['base']['sha']
            builds.append(dict(build, id=12, created_at='2026-11-21T00:01:00Z',
                               run_started_at='2026-11-21T00:01:00Z', conclusion='failure'))
            with self.assertRaises(InvalidPreviewArtifact): publish('owner/repo', self.root, self.root)
            self.assertEqual(active_site(self.root), first)
            builds.pop()
            review['approved'] = False
            with self.assertRaises(InvalidPreviewArtifact): publish('owner/repo', self.root, self.root)
            self.assertEqual(active_site(self.root), first)


if __name__ == '__main__':
    unittest.main()
