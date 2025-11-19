'use client';

import { useEffect } from 'react';
import { CheckCircle, AlertCircle, X } from 'lucide-react';

interface ToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  duration?: number;
  onClose?: () => void;
}

export function Toast({ message, type = 'info', duration = 4000, onClose }: ToastProps) {
  useEffect(() => {
    if (duration && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const bgColor =
    type === 'success'
      ? 'bg-green-50 border-green-200'
      : type === 'error'
        ? 'bg-red-50 border-red-200'
        : 'bg-blue-50 border-blue-200';

  const textColor =
    type === 'success'
      ? 'text-green-800'
      : type === 'error'
        ? 'text-red-800'
        : 'text-blue-800';

  const iconColor = type === 'success' ? 'text-green-600' : type === 'error' ? 'text-red-600' : 'text-blue-600';

  return (
    <div
      className={`fixed bottom-4 right-4 flex items-start gap-3 p-4 rounded-lg border max-w-md shadow-lg animate-in slide-in-from-right-4 ${bgColor}`}
    >
      {type === 'success' ? (
        <CheckCircle size={20} className={`flex-shrink-0 mt-0.5 ${iconColor}`} />
      ) : (
        <AlertCircle size={20} className={`flex-shrink-0 mt-0.5 ${iconColor}`} />
      )}
      <p className={`text-sm font-medium flex-1 ${textColor}`}>{message}</p>
      {onClose && (
        <button
          onClick={onClose}
          className={`flex-shrink-0 ${textColor} hover:opacity-75 transition-opacity`}
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}
