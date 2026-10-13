export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(`Request failed (${response.status}). Please try again.`);
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const getTasks = () => request<Task[]>('/api/tasks');
export const setCompleted = (id: number, completed: boolean) => request<Task>(`/api/tasks/${id}`, {
  method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ completed }),
});
export const deleteTask = (id: number) => request<void>(`/api/tasks/${id}`, { method: 'DELETE' });
