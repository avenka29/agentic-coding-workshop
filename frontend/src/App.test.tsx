import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import App from './App';

const task = { id: 1, title: 'Read contract', description: 'Shared boundary', completed: false };
let container: HTMLDivElement;
let root: Root;
let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  container = document.createElement('div');
  document.body.append(container);
  root = createRoot(container);
  fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
});
afterEach(async () => { await act(async () => root.unmount()); container.remove(); vi.unstubAllGlobals(); });
function respond(body: unknown, status = 200) {
  return { ok: status < 400, status, json: async () => body };
}
async function render() { await act(async () => root.render(<App />)); }

test('lists tasks, toggles completion, and deletes', async () => {
  fetchMock.mockResolvedValueOnce(respond([task]));
  await render();
  expect(container.textContent).toContain('Read contract');
  expect(container.textContent).toContain('Shared boundary');
  fetchMock.mockResolvedValueOnce(respond({ ...task, completed: true }));
  await act(async () => container.querySelector<HTMLInputElement>('input')!.click());
  expect(fetchMock).toHaveBeenLastCalledWith('/api/tasks/1', expect.objectContaining({ method: 'PATCH', body: '{"completed":true}' }));
  expect(container.querySelector<HTMLInputElement>('input')!.checked).toBe(true);
  fetchMock.mockResolvedValueOnce(respond(undefined, 204));
  await act(async () => container.querySelector<HTMLButtonElement>('button')!.click());
  expect(fetchMock).toHaveBeenLastCalledWith('/api/tasks/1', { method: 'DELETE' });
  expect(container.textContent).toContain('No tasks yet.');
});

test('shows loading and recovers from a failed list request', async () => {
  let resolve!: (value: unknown) => void;
  fetchMock.mockReturnValueOnce(new Promise(done => { resolve = done; }));
  await render();
  expect(container.querySelector('[role=status]')?.textContent).toContain('Loading');
  await act(async () => resolve(respond({}, 500)));
  expect(container.querySelector('[role=alert]')?.textContent).toContain('500');
  fetchMock.mockResolvedValueOnce(respond([task]));
  await act(async () => container.querySelector<HTMLButtonElement>('button')!.click());
  expect(container.querySelector('[role=alert]')).toBeNull();
  expect(container.textContent).toContain(task.title);
});

test('keeps the task when deletion fails', async () => {
  fetchMock.mockResolvedValueOnce(respond([task]));
  await render();
  fetchMock.mockResolvedValueOnce(respond({}, 500));
  await act(async () => container.querySelector<HTMLButtonElement>('button')!.click());
  expect(container.querySelector('[role=alert]')).not.toBeNull();
  expect(container.textContent).toContain(task.title);
});
