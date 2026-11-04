export const verdicts = {
  AC: ['答案正确', 'success'], WA: ['答案错误', 'danger'], TLE: ['运行超时', 'warning'],
  RE: ['运行错误', 'danger'], CE: ['编译错误', 'warning'], OLE: ['输出超限', 'warning'],
  SE: ['评测异常', 'danger'], QUEUED: ['等待评测', 'neutral'], RUNNING: ['正在评测', 'neutral'],
  INTERRUPTED: ['服务中断', 'warning'], RUN: ['运行完成', 'neutral'],
};
export const escapeHtml = (value = '') => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export function safeUrl(value) {
  try { const u = new URL(value); return ['http:', 'https:'].includes(u.protocol) ? u.href : ''; } catch { return ''; }
}
export function localEndpoint(value) {
  const url = new URL(value);
  if (!['http:', 'https:'].includes(url.protocol) || !['localhost', '127.0.0.1', '[::1]'].includes(url.hostname) || url.username || url.password) throw Error('判题地址必须是本机 localhost 或 127.0.0.1');
  if (url.pathname !== '/' || url.search || url.hash) throw Error('判题地址只填写协议、主机和端口');
  return url.origin;
}
export function filterProblems(problems, { category = '', query = '', difficulty = '', status = '', progress = {} } = {}) {
  const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  return problems.filter(p => (!category || p.category === category)
    && (!difficulty || p.difficulty === difficulty)
    && (!status || (status === 'AC' ? progress[p.id] === 'AC' : status === 'untried' ? !progress[p.id] : progress[p.id] && progress[p.id] !== 'AC'))
    && words.every(word => [p.id, p.title, p.category, ...(p.tags || [])].join(' ').toLowerCase().includes(word)));
}
export function mergeCatalog(builtin, local) {
  return [...new Map([...builtin, ...local].map(p => [p.id, p])).values()];
}
