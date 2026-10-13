import { useEffect, useState } from 'react';
import { deleteTask, getTasks, setCompleted, type Task } from './api';

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);
    setError('');
    try { setTasks(await getTasks()); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Unable to load tasks.'); }
    finally { setLoading(false); }
  }
  useEffect(() => { void load(); }, []);

  async function change(task: Task, remove = false) {
    setBusy(true);
    setError('');
    try {
      if (remove) {
        await deleteTask(task.id);
        setTasks(current => current.filter(item => item.id !== task.id));
      } else {
        const updated = await setCompleted(task.id, !task.completed);
        setTasks(current => current.map(item => item.id === task.id ? updated : item));
      }
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Unable to update task.'); }
    finally { setBusy(false); }
  }

  return <main>
    <header><p className="eyebrow">Agentic coding workshop</p><h1>Your tasks</h1>
      <p>Small tasks. Independent agents. One shared contract.</p></header>
    <aside>Workshop exercise: add task creation with a frontend agent and a backend agent.</aside>
    {error && <div role="alert">{error} <button disabled={busy || loading} onClick={() => void load()}>Reload tasks</button></div>}
    {loading ? <p role="status">Loading tasks…</p> : <>
      <p className="summary">{tasks.filter(task => task.completed).length} of {tasks.length} complete</p>
      {tasks.length === 0 && <p>No tasks yet.</p>}
      <ul>{tasks.map(task => <li key={task.id}>
        <label><input type="checkbox" checked={task.completed} disabled={busy} onChange={() => void change(task)} />
          <span className={task.completed ? 'completed' : ''}><strong>{task.title}</strong><span className="description">{task.description}</span></span></label>
        <button disabled={busy} aria-label={`Delete ${task.title}`} onClick={() => void change(task, true)}>Delete</button>
      </li>)}</ul>
    </>}
  </main>;
}
