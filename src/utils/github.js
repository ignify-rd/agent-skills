const REPO = 'ignify-rd/agent-skills';
const API_BASE = 'https://api.github.com';

export async function fetchReleases() {
  const res = await fetch(`${API_BASE}/repos/${REPO}/releases`, {
    headers: { 'Accept': 'application/vnd.github+json' },
  });
  if (!res.ok) throw new Error(`GitHub API error: ${res.status}`);
  return res.json();
}

export async function getLatestRelease() {
  const res = await fetch(`${API_BASE}/repos/${REPO}/releases/latest`, {
    headers: { 'Accept': 'application/vnd.github+json' },
  });
  if (!res.ok) throw new Error(`GitHub API error: ${res.status}`);
  return res.json();
}
