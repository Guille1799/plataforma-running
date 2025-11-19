import React from 'react';

interface SpinnerProps {
  className?: string;
}

export function Spinner({ className }: SpinnerProps) {
  return (
    <div className={`inline-block ${className}`}>
      <div className="relative w-10 h-10">
        <div className="absolute inset-0 border-4 border-slate-600 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-transparent border-t-blue-500 border-r-blue-500 rounded-full animate-spin"></div>
      </div>
    </div>
  );
}
