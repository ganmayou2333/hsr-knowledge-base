/* Trusted parent: untrusted PR files are JSON objects and run only in an opaque iframe. */
(() => {
  const REPO = 'ganmayou2333/hsr-knowledge-base';
  // Pages snapshots can lag behind permission changes; never treat them as live.
  const SNAPSHOT_MAX_AGE_MS = 15 * 60 * 1000;
  const number = new URLSearchParams(location.search).get('pr');
  const status = document.getElementById('status');
  const main = document.querySelector('main');
  const label = document.getElementById('pr-label');
  const reviewLabel = document.getElementById('review-label');
  const link = document.getElementById('pr-link');
  let frame = document.getElementById('preview');
  let manifest, bridge, verified = false, hasPage = false, currentPage = 'index.html';
  let externalApprovalRequired = false;
  let externalApprovalExpires = 0;
  let requests = 0, activeReads = 0, bytesRead = 0, generation = 0, verification = 0, reviewCheck = 0;
  let liveServiceSeen = document.querySelector('meta[name="preview-service"][content="enabled"]') !== null, liveExpiry = 0;
  const waiters = [];
  const objectCache = new Map();
  const mime = {js: 'text/javascript', css: 'text/css', png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', webp: 'image/webp'};

  function fail(message) {
    externalApprovalExpires = 0;
    liveExpiry++;
    verification++;
    verified = false;
    hasPage = false;
    generation++;
    reviewCheck++;
    reviewLabel.textContent = '未经人工审查';
    frame.hidden = true;
    status.textContent = message;
  }

  function validLiveProof(proof) {
    const age = Date.now() - proof.captured_at * 1000;
    return proof.source === 'service-v1' && proof.repo === REPO && proof.pr === Number(number) &&
      proof.head === manifest.head && Number.isSafeInteger(proof.captured_at) &&
      age >= -5000 && age < 30000 && typeof proof.approved === 'boolean' &&
      proof.preview?.head === manifest.head && proof.preview?.base === manifest.base &&
      proof.preview?.run === manifest.run && proof.preview?.run_attempt === manifest.run_attempt && proof.preview?.trusted_run === manifest.trusted_run &&
      proof.preview?.trusted_attempt === manifest.trusted_attempt && proof.preview?.valid === true;
  }

  function showLiveReview(proof, check) {
    if (proof.approved !== true) return;
    reviewLabel.textContent = '已有有效人工批准';
    const remaining = proof.captured_at * 1000 + 30000 - Date.now();
    setTimeout(() => { if (check === reviewCheck) reviewLabel.textContent = '未经人工审查'; }, Math.max(0, remaining));
  }

  function armLiveExpiry(proof) {
    const token = ++liveExpiry;
    const remaining = proof.captured_at * 1000 + 30000 - Date.now();
    setTimeout(() => {
      if (token !== liveExpiry || !verified) return;
      verification++;
      fail('无法验证当前提交或检查结果，预览暂不可用。');
    }, Math.max(0, remaining));
  }

  async function refreshReview(allowPending = false) {
    if (!verified && !allowPending) return;
    const check = ++reviewCheck;
    reviewLabel.textContent = '未经人工审查';
    try {
      const proof = await json(`previews/${number}/review.json`);
      if (proof.source === 'service-v1') {
        liveServiceSeen = true;
        if (check !== reviewCheck || !verified) return;
        if (!validLiveProof(proof)) {
          verification++;
          return fail('无法验证当前提交或检查结果，预览暂不可用。');
        }
        armLiveExpiry(proof);
        showLiveReview(proof, check);
        return;
      }
      if (liveServiceSeen) throw new Error('Preview service unavailable');
      const expires = proof.captured_at * 1000 + SNAPSHOT_MAX_AGE_MS;
      if (proof.repo !== REPO || proof.pr !== Number(number) || proof.head !== manifest.head ||
          proof.approved !== true || !Number.isSafeInteger(proof.captured_at) ||
          expires <= Date.now() || proof.captured_at * 1000 > Date.now() + 5000 ||
          !Array.isArray(proof.reviews) || proof.reviews.length > 1000) throw new Error('Unverified review');
      const reviews = [];
      for (let page = 1; page <= 11; page++) {
        const batch = await json(`https://api.github.com/repos/${REPO}/pulls/${number}/reviews?per_page=100&page=${page}`);
        if (!Array.isArray(batch) || batch.length > 100 || reviews.length + batch.length > 1000) throw new Error('Invalid reviews');
        reviews.push(...batch);
        if (batch.length < 100) break;
        if (page === 11) throw new Error('Too many reviews');
      }
      const evidence = reviews.map(item => [item.id, item.state, item.user?.login ?? null,
        item.user?.type ?? null, item.commit_id ?? null, item.submitted_at ?? null]).sort((a, b) => a[0] - b[0]);
      const [pr, branch] = await Promise.all([
        json(`https://api.github.com/repos/${REPO}/pulls/${number}`),
        json(`https://api.github.com/repos/${REPO}/branches/main`)
      ]);
      if (check !== reviewCheck || (!verified && !allowPending)) return;
      if (pr.state !== 'open' || pr.head?.sha !== manifest.head || pr.base?.sha !== manifest.base ||
          pr.base?.ref !== 'main' || pr.base?.repo?.full_name?.toLowerCase() !== REPO.toLowerCase() ||
          branch.name !== 'main' || branch.commit?.sha !== manifest.base) {
        verification++;
        return fail('无法验证当前提交或检查结果，预览暂不可用。');
      }
      if (expires <= Date.now() || JSON.stringify(evidence) !== JSON.stringify(proof.reviews)) throw new Error('Review changed');
      reviewLabel.textContent = '已有人工批准（快照，可能延迟）';
      if (externalApprovalRequired) externalApprovalExpires = expires;
      setTimeout(() => {
        if (externalApprovalRequired && externalApprovalExpires === expires) {
          fail('外部 PR 的批准无法验证，预览暂不可用。');
        } else if (!externalApprovalRequired && check === reviewCheck) reviewLabel.textContent = '未经人工审查';
      }, Math.max(0, expires - Date.now()));
      return true;
    } catch {
      if (check === reviewCheck && (liveServiceSeen || externalApprovalRequired)) {
        verification++;
        fail('无法验证当前提交或检查结果，预览暂不可用。');
      } else if (check === reviewCheck) reviewLabel.textContent = '未经人工审查';
    }
  }

  async function json(url) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(url, {cache: 'no-store', credentials: 'omit', redirect: 'error', signal: controller.signal});
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return await response.json();
    } finally { clearTimeout(timeout); }
  }

  async function latestRun(workflow, event) {
    const path = `.github/workflows/${workflow}`;
    let latest = null, pending = null, latestStarted = null, tiedStarted = false, total = 0;
    const ids = new Set(), dates = new Set();
    for (let page = 1; page <= 11; page++) {
      const result = await json(`https://api.github.com/repos/${REPO}/actions/workflows/${workflow}/runs?event=${event}&head_sha=${manifest.head}&per_page=100&page=${page}`);
      const runs = result.workflow_runs;
      if (!Array.isArray(runs) || runs.length > 100 || (page === 11 && runs.length)) throw new Error('Invalid run list');
      total += runs.length;
      if (total >= 1000) throw new Error('Run list may be incomplete');
      for (const run of runs) {
        if (run.event !== event || run.path !== path || run.head_sha !== manifest.head) continue;
        if (!Array.isArray(run.pull_requests) || !run.pull_requests.length) throw new Error('Unbound workflow run');
        const matches = run.pull_requests.filter(item => item.number === Number(number));
        if (!matches.length) continue;
        if (matches.length !== 1 || !Number.isSafeInteger(run.id) || run.id < 1 ||
            ids.has(run.id) || dates.has(run.created_at) ||
            ![run.created_at, run.run_started_at].every(value => typeof value === 'string' &&
              /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(value) &&
              Number.isFinite(Date.parse(value)) && new Date(value).toISOString() === value.replace('Z', '.000Z')) ||
            run.run_started_at < run.created_at) throw new Error('Invalid workflow run');
        ids.add(run.id); dates.add(run.created_at);
        if (run.status !== 'completed') pending = run;
        if (!latest || run.created_at > latest.created_at) latest = run;
        if (latestStarted === null || run.run_started_at > latestStarted) {
          latestStarted = run.run_started_at; tiedStarted = false;
        } else if (run.run_started_at === latestStarted) tiedStarted = true;
      }
      if (runs.length < 100) {
        if (pending) return pending;
        if (latest && (latest.run_started_at !== latestStarted || tiedStarted)) throw new Error('Ambiguous latest attempt');
        return latest;
      }
    }
    throw new Error('Too many workflow runs');
  }

  async function object(path, kind) {
    if (!manifest || !Object.prototype.hasOwnProperty.call(manifest.files, path)) return null;
    const digest = manifest.files[path];
    if (typeof digest !== 'string' || !/^[0-9a-f]{64}$/.test(digest)) return null;
    const extension = path.split('.').pop().toLowerCase();
    if (kind === 'page' && extension !== 'html') return null;
    if (kind === 'script' && extension !== 'js') return null;
    if (kind === 'style' && extension !== 'css') return null;
    if (kind === 'image' && !['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(extension)) return null;
    if (!['page', 'script', 'style', 'image'].includes(kind)) return null;
    if (!objectCache.has(digest)) {
      const promise = (async () => {
        if (activeReads >= 4) await new Promise(resolve => waiters.push(resolve));
        else activeReads++;
        try {
        const value = await json(`previews/${number}/objects/${digest}.json`);
        if (typeof value.data !== 'string' || value.data.length > 24 * 1024 * 1024 || !/^[A-Za-z0-9+/]*={0,2}$/.test(value.data)) throw new Error('Invalid object');
        const binary = atob(value.data);
        const bytes = Uint8Array.from(binary, c => c.charCodeAt(0));
        bytesRead += bytes.length;
        if (bytesRead > 128 * 1024 * 1024) throw new Error('Preview exceeds memory budget');
        const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), b => b.toString(16).padStart(2, '0')).join('');
        if (hash !== digest) throw new Error('Object digest mismatch');
        return {base64: value.data, bytes};
        } finally {
          const next = waiters.shift();
          if (next) next();
          else activeReads--;
        }
      })();
      objectCache.set(digest, promise);
      promise.catch(() => { if (objectCache.get(digest) === promise) objectCache.delete(digest); });
    }
    const result = await objectCache.get(digest);
    if (kind === 'page') return new TextDecoder('utf-8', {fatal: true}).decode(result.bytes);
    return `data:${mime[extension]};base64,${result.base64}`;
  }

  async function verify() {
    const attempt = ++verification;
    reviewCheck++;
    reviewLabel.textContent = '未经人工审查';
    verified = false;
    generation++;
    frame.hidden = true;
    try {
      let proof;
      try { proof = await json(`previews/${number}/review.json`); } catch {}
      if (attempt !== verification) return false;
      if (proof?.source === 'service-v1') {
        liveServiceSeen = true;
        if (!validLiveProof(proof)) throw new Error('Preview is stale');
        verified = true;
        armLiveExpiry(proof);
        status.textContent = '当前提交的自动检查已通过；预览内容由 PR 提供。';
        frame.hidden = false;
        showLiveReview(proof, reviewCheck);
        return true;
      }
      if (liveServiceSeen) throw new Error('Preview service unavailable');
      const [pr, branch, run, workflow, trustedRun, latestBuild, latestTrusted] = await Promise.all([
        json(`https://api.github.com/repos/${REPO}/pulls/${number}`),
        json(`https://api.github.com/repos/${REPO}/branches/main`),
        json(`https://api.github.com/repos/${REPO}/actions/runs/${manifest.run}`),
        json(`https://api.github.com/repos/${REPO}/actions/workflows/wiki-trusted-data.yml`),
        json(`https://api.github.com/repos/${REPO}/actions/runs/${manifest.trusted_run}`),
        latestRun('wiki-quality.yml', 'pull_request'),
        latestRun('wiki-trusted-data.yml', 'pull_request_target')
      ]);
      const associated = Array.isArray(run.pull_requests) && run.pull_requests.some(item =>
        item.number === Number(number) && item.head?.sha === manifest.head && item.base?.sha === manifest.base);
      const trustedAssociated = Array.isArray(trustedRun.pull_requests) && trustedRun.pull_requests.filter(item =>
        item.number === Number(number) && item.head?.sha === manifest.head && item.base?.sha === manifest.base &&
        item.head?.repo?.id === pr.head?.repo?.id && item.base?.repo?.id === pr.base?.repo?.id).length === 1;
      if (attempt !== verification) return false;
      if (pr.state !== 'open' || pr.head?.sha !== manifest.head || pr.base?.sha !== manifest.base ||
          pr.base?.ref !== 'main' || pr.base?.repo?.full_name?.toLowerCase() !== REPO.toLowerCase() ||
          branch.name !== 'main' || branch.commit?.sha !== manifest.base ||
          run.id !== manifest.run || run.run_attempt !== manifest.run_attempt || run.event !== 'pull_request' || run.conclusion !== 'success' || run.head_sha !== manifest.head ||
          run.path !== '.github/workflows/wiki-quality.yml' || !associated ||
          latestBuild?.id !== manifest.run || latestBuild?.run_attempt !== manifest.run_attempt ||
          latestBuild?.status !== 'completed' || latestBuild?.conclusion !== 'success' ||
          latestTrusted?.id !== manifest.trusted_run || latestTrusted?.run_attempt !== manifest.trusted_attempt ||
          latestTrusted?.status !== 'completed' || latestTrusted?.conclusion !== 'success' ||
          workflow.state !== 'active' || workflow.path !== '.github/workflows/wiki-trusted-data.yml' ||
          !Number.isSafeInteger(workflow.id) || workflow.id < 1 ||
          !Number.isSafeInteger(pr.head?.repo?.id) || pr.head.repo.id < 1 ||
          !Number.isSafeInteger(pr.base?.repo?.id) || pr.base.repo.id < 1 ||
          trustedRun.id !== manifest.trusted_run || trustedRun.workflow_id !== workflow.id ||
          trustedRun.repository?.id !== pr.base.repo.id || trustedRun.run_attempt !== manifest.trusted_attempt ||
          trustedRun.event !== 'pull_request_target' || trustedRun.status !== 'completed' ||
          trustedRun.conclusion !== 'success' || trustedRun.path !== workflow.path ||
          trustedRun.head_sha !== manifest.head || !trustedAssociated) {
        throw new Error('Preview is stale');
      }
      externalApprovalRequired = pr.head.repo.id !== pr.base.repo.id;
      if (externalApprovalRequired && !await refreshReview(true)) throw new Error('External approval unavailable');
      if (attempt !== verification) return false;
      verified = true;
      status.textContent = '当前提交的自动检查已通过；预览内容由 PR 提供。';
      frame.hidden = false;
      if (!externalApprovalRequired) refreshReview();
      return true;
    } catch {
      if (attempt !== verification) return false;
      fail('无法验证当前提交或检查结果，预览暂不可用。');
      return false;
    }
  }

  async function navigate(path) {
    if (!verified || typeof path !== 'string' || path.length > 1024) return;
    const navigation = ++generation;
    try {
      const html = await object(path, 'page');
      if (!verified || navigation !== generation) return;
      if (html === null) throw new Error('Page missing');
      currentPage = path;
      requests = 0;
      const next = document.createElement('iframe');
      next.id = 'preview';
      next.title = 'Wiki 预览内容';
      next.setAttribute('sandbox', 'allow-scripts');
      next.referrerPolicy = 'no-referrer';
      next.hidden = !verified;
      const policy = "default-src 'none'; script-src 'unsafe-inline' data:; style-src 'unsafe-inline' data:; img-src data:; font-src data:; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'";
      next.srcdoc = `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="${policy}"><script data-bridge src="data:text/javascript;base64,${bridge}"><\/script></head><body><p>正在加载页面…</p></body></html>`;
      next.dataset.html = html;
      frame.replaceWith(next);
      frame = next;
      hasPage = true;
    } catch { if (navigation === generation) fail('预览页面无法读取或校验失败。'); }
  }

  addEventListener('message', async event => {
    if (!verified || event.source !== frame.contentWindow || !event.data || typeof event.data !== 'object') return;
    const message = event.data;
    if (message.type === 'preview:ready') {
      frame.contentWindow.postMessage({type: 'preview:init', html: frame.dataset.html, page: currentPage}, '*');
      delete frame.dataset.html;
    } else if (message.type === 'preview:navigate' && typeof message.path === 'string') {
      await navigate(message.path);
    } else if (message.type === 'preview:read' && Number.isSafeInteger(message.id) && typeof message.path === 'string' && ++requests <= 1024) {
      const source = event.source;
      let url = null;
      try { url = await object(message.path, message.kind); } catch {}
      if (source === frame.contentWindow) source.postMessage({type: 'preview:result', id: message.id, url}, '*');
    } else if (message.type === 'preview:error') {
      fail('预览页面无法显示。');
    }
  });

  async function start() {
    if (!/^[1-9][0-9]{0,7}$/.test(number || '')) return fail('请指定有效的 PR 编号。');
    label.textContent = 'PR #' + number;
    link.href = `https://github.com/${REPO}/pull/${number}`;
    try {
      manifest = await json(`previews/${number}/manifest.json`);
      if (manifest.version !== 1 || manifest.repo !== REPO || manifest.pr !== Number(number) ||
          !/^[0-9a-f]{40}$/.test(manifest.head) || !/^[0-9a-f]{40}$/.test(manifest.base) ||
          !Number.isSafeInteger(manifest.run) || manifest.run < 1 || !Number.isSafeInteger(manifest.run_attempt) || manifest.run_attempt < 1 ||
          !Number.isSafeInteger(manifest.trusted_run) || manifest.trusted_run < 1 ||
          !Number.isSafeInteger(manifest.trusted_attempt) || manifest.trusted_attempt < 1 ||
          !manifest.files || typeof manifest.files !== 'object') throw new Error('Invalid manifest');
      const response = await fetch('frame.js', {cache: 'no-store', credentials: 'omit'});
      if (!response.ok) throw new Error('Missing trusted bridge');
      const source = await response.text();
      bridge = btoa(String.fromCharCode(...new TextEncoder().encode(source)));
      const verifyAndLoad = async () => {
        if (await verify() && !hasPage) await navigate('index.html');
      };
      await verifyAndLoad();
      setInterval(verifyAndLoad, 90000);
      setInterval(refreshReview, 15000);
      document.addEventListener('visibilitychange', () => { if (!document.hidden) verifyAndLoad(); });
    } catch { fail('预览尚未生成或数据无效。'); }
  }
  start();
})();
