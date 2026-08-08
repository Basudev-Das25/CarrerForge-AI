/**
 * Toast notification system.
 * Usage: import { toast } from "@/components/common/Toast";
 * toast.success("Saved!");
 * toast.error("Something went wrong");
 */

import { useState, useEffect, useCallback } from "react";

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
    // Immediately call the listener with the current toasts
    listener([...toasts]);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  },
  dismiss: remove,
};

export function useToasts() {
  const [currentToasts, setCurrentToasts] = useState<Toast[]>(toasts);

  useEffect(() => {
    const unsubscribe = toast.subscribe(setCurrentToasts);
    return unsubscribe;
  }, []);

  const dismiss = useCallback((id: string) => {
    remove(id);
  }, []);

  return { toasts: currentToasts, dismiss };
}

export function ToastContainer() {
  const { toasts, dismiss } = useToasts();
  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`rounded-lg px-4 py-3 text-sm shadow-lg transition-all ${
            t.type === "success" ? "bg-green-600 text-white" :
            t.type === "error" ? "bg-red-600 text-white" :
            t.type === "warning" ? "bg-amber-500 text-white" :
            "bg-surface-2 text-text-primary"
          }`}
        >
          <div className="flex items-center justify-between gap-4">
            <span>{t.message}</span>
            <button onClick={() => dismiss(t.id)} className="text-current opacity-70 hover:opacity-100">&times;</button>
          </div>
        </div>
      ))}
    </div>
  );
}
