"""Exercise the review service over HTTP without GitHub credentials."""
import json
import subprocess
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
from pathlib import Path

from tools.preview_review_server import ReviewServer
from tools.test_reconcile_previews import PR, BUILD, TRUSTED

HEAD = 'a' * 40


class ReviewServerTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.state = 'approved'
        def reader(repo, number):
            self.calls.append((repo, number))
            if self.state == 'failure':
                raise subprocess.CalledProcessError(1, 'gh')
            return {'pr': number, 'head': HEAD, 'approved': self.state == 'approved',
                    'reviews': [], 'captured_at': int(time.time())}
        self.server = ReviewServer(('127.0.0.1', 0), 'owner/repo', reader=reader)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close)
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=5) as response:
                return response.status, json.loads(response.read()), response.headers
        except urllib.error.HTTPError as response:
            with response:
                return response.code, json.loads(response.read()), response.headers

    def test_valid_request_is_read_only_bounded_and_not_browser_cached(self):
        status, body, headers = self.get('/previews/37/review.json')
        self.assertEqual(status, 200)
        self.assertTrue(body['approved'])
        self.assertEqual((body['repo'], body['pr'], body['head']), ('owner/repo', 37, HEAD))
        self.assertEqual(headers['Cache-Control'], 'no-store, max-age=0')
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.get('/previews/37/review.json')
        self.assertEqual(len(self.calls), 1)
        self.server.cache[37]['captured_at'] -= 11
        self.state = 'revoked'
        self.assertFalse(self.get('/previews/37/review.json')[1]['approved'])
        self.assertEqual(len(self.calls), 2)

    def test_failure_and_invalid_paths_never_show_approval(self):
        self.state = 'failure'
        status, body, _ = self.get('/previews/37/review.json')
        self.assertEqual((status, body), (503, {'error': 'Review status unavailable'}))
        for path in ['/previews/0/review.json', '/previews/1/review.json?repo=elsewhere', '/previews/../review.json']:
            self.assertEqual(self.get(path)[0], 404)
        self.assertEqual(len(self.calls), 1)
        self.state = 'revoked'
        self.assertFalse(self.get('/previews/37/review.json')[1]['approved'])

    def test_invalid_snapshot_and_busy_service_fail_closed(self):
        self.server.reader = lambda repo, number: {'pr': number, 'approved': True, 'head': 'wrong'}
        self.assertEqual(self.get('/previews/37/review.json')[0], 503)
        self.server.lock.acquire()
        try:
            self.assertEqual(self.get('/previews/37/review.json')[0], 503)
        finally:
            self.server.lock.release()

    def test_static_viewer_serves_only_allowed_paths_and_dynamic_review(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / 'index.html').write_text('<head></head><h1>trusted</h1>', encoding='utf-8')
            (site / 'shell.js').write_text('trusted', encoding='utf-8')
            bundle = site / 'previews' / '37'
            (bundle / 'objects').mkdir(parents=True)
            (bundle / 'manifest.json').write_text(json.dumps({'version': 1, 'repo': 'owner/repo', 'pr': 37,
                'head': HEAD, 'base': 'b' * 40, 'run': 1, 'run_attempt': 1, 'trusted_run': 2, 'trusted_attempt': 1, 'files': {'index.html': 'a' * 64}}), encoding='ascii')
            (bundle / 'review.json').write_text('{"approved":false}', encoding='ascii')
            (bundle / 'source.html').write_text('<script>bad</script>', encoding='ascii')
            digest = 'a' * 64
            (bundle / 'objects' / f'{digest}.json').write_text('{"data":""}', encoding='ascii')
            self.server.site = site
            self.server.validator = lambda repo, number, manifest: True
            with urllib.request.urlopen(self.base + '/?pr=37', timeout=5) as response:
                self.assertEqual(response.read(), b'<head><meta name="preview-service" content="enabled"></head><h1>trusted</h1>')
                self.assertEqual(response.headers['Content-Security-Policy'], "frame-src 'none'")
            self.assertEqual(self.get('/previews/37/manifest.json')[0], 200)
            self.assertEqual(self.get(f'/previews/37/objects/{digest}.json')[0], 200)
            review = self.get('/previews/37/review.json')[1]
            self.assertTrue(review['approved'])
            self.assertEqual(review['source'], 'service-v1')
            self.assertTrue(review['preview']['valid'])
            for path in ['/previews/37/source.html', '/previews/37/objects/../review.json',
                         '/previews/37/objects/invalid.json', '/shell.js?x=1']:
                self.assertEqual(self.get(path)[0], 404)

    def test_static_files_cannot_be_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            target = site / 'target'
            target.write_text('secret', encoding='utf-8')
            try:
                (site / 'shell.js').symlink_to(target)
            except OSError as error:
                self.skipTest(f'symlink unavailable: {error}')
            self.server.site = site
            self.assertEqual(self.get('/shell.js')[0], 404)

    def test_live_status_rejects_stale_or_unverifiable_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            bundle = site / 'previews' / '37'
            bundle.mkdir(parents=True)
            manifest_path = bundle / 'manifest.json'
            manifest_path.write_text(json.dumps({'version': 1, 'repo': 'owner/repo', 'pr': 37,
                'head': HEAD, 'base': 'b' * 40, 'run': 1, 'run_attempt': 1, 'trusted_run': 2, 'trusted_attempt': 1, 'files': {'index.html': 'a' * 64}}), encoding='ascii')
            self.server.site = site
            self.server.validator = lambda repo, number, manifest: False
            status, body, _ = self.get('/previews/37/review.json')
            self.assertEqual(status, 200)
            self.assertFalse(body['preview']['valid'])
            self.server.cache.clear()

            def failure(repo, number, manifest):
                raise subprocess.CalledProcessError(1, 'gh')
            self.server.validator = failure
            self.assertEqual(self.get('/previews/37/review.json')[0], 503)
            self.assertNotIn(37, self.server.cache)
            manifest_path.write_text('{}', encoding='ascii')
            self.assertEqual(self.get('/previews/37/review.json')[0], 503)
            self.assertNotIn(37, self.server.cache)

    def test_live_service_rechecks_latest_runs_and_external_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            bundle = site / 'previews' / '7'
            bundle.mkdir(parents=True)
            (bundle / 'manifest.json').write_text(json.dumps({'version': 1, 'repo': 'owner/repo', 'pr': 7,
                'head': HEAD, 'base': 'b' * 40, 'run': 10, 'run_attempt': 1, 'trusted_run': 11,
                'trusted_attempt': 1, 'files': {'index.html': 'a' * 64}}), encoding='ascii')
            self.server.site = site
            build = dict(BUILD, run_attempt=1)
            builds = [build]
            pr = dict(PR)
            def api(path, paginate=False):
                if path.endswith('/pulls/7'): return pr
                if '/wiki-quality.yml/runs?' in path: return [{'workflow_runs': builds}]
                if '/wiki-trusted-data.yml/runs?' in path: return [{'workflow_runs': [TRUSTED]}]
                raise AssertionError(path)
            with patch('tools.verify_preview_publication.gh_api', side_effect=api), \
                 patch('tools.verify_preview_publication.metadata', return_value=True), \
                 patch('tools.verify_preview_publication.snapshot', return_value={'head': HEAD, 'approved': False}):
                self.assertEqual(self.get('/previews/7/review.json')[0], 200)
                self.server.cache.clear()
                builds.append(dict(build, id=12, conclusion='failure', created_at='2026-11-21T00:01:00Z', run_started_at='2026-11-21T00:01:00Z'))
                self.assertEqual(self.get('/previews/7/review.json')[0], 503)
                builds.pop()
                pr['head'] = {'sha': HEAD, 'repo': {'id': 2}}
                self.assertEqual(self.get('/previews/7/review.json')[0], 503)


if __name__ == '__main__': unittest.main()
