/**
 * Toast notification system.
 * Usage: import { toast } from "@/components/common/Toast";
 * toast.success("Saved!");
 * toast.error("Something went wrong");
 */

type ToastType = "success" | "error" | "info" | "warning";

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

let listeners: Array<(toasts: Toast[]) => void> = [];
let toasts: Toast[] = [];

function notify() {
  listeners.forEach((l) => l([...toasts]));
}

function add(type: ToastType, message: string) {
  const id = Math.random().toString(36).slice(2);
  toasts = [...toasts, { id, type, message }];
  notify();
  setTimeout(() => remove(id), 4000);
}

function remove(id: string) {
  toasts = toasts.filter((t) => t.id !== id);
  notify();
}

export const toast = {
  success: (message: string) => add("success", message),
  error: (message: string) => add("error", message),
  info: (message: string) => add("info", message),
  warning: (message: string) => add("warning", message),
  subscribe: (listener: (toasts: Toast[]) => void) => {
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  },
  dismiss: remove,
};

export function ToastContainer() {
  // This is a simple hook-based container
  // In a real app you'd use a useState hook here
  return null; // Will be wired up with a proper hook below
}

export function useToasts() {
  // This is a simplified version — in production, use useState + useEffect
  return { toasts, dismiss: remove };
}
