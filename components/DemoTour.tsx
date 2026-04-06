'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronRight, ChevronLeft, Sparkles } from 'lucide-react';

const TOUR_KEY = 'demo_tour_seen';
const DEMO_EMAIL = process.env.NEXT_PUBLIC_DEMO_EMAIL?.trim() ?? '';

interface TourStep {
  title: string;
  description: string;
  icon: string;
  href: string;
}

const STEPS: TourStep[] = [
  {
    icon: '📊',
    title: 'Dashboard',
    description:
      'Your training hub — weekly volume, performance trends, heart rate zones, and AI-powered smart suggestions all in one place.',
    href: '/dashboard',
  },
  {
    icon: '🏃',
    title: 'Workouts',
    description:
      'Every run logged automatically from Garmin with FIT-file precision: pace, cadence, HR zones, running dynamics and more.',
    href: '/workouts',
  },
  {
    icon: '📋',
    title: 'Training Plans',
    description:
      'AI-generated multi-week plans tailored to your goal (5K → marathon), fitness level and schedule. Adapts week by week.',
    href: '/training-plans',
  },
  {
    icon: '🤖',
    title: 'AI Coach',
    description:
      'Chat with your personalised running coach. Ask about recovery, race strategy, injury prevention — it knows your data.',
    href: '/coach',
  },
];

export function DemoTour() {
  const [visible, setVisible] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (!DEMO_EMAIL) return;
    const seen = localStorage.getItem(TOUR_KEY);
    if (!seen) setVisible(true);
  }, []);

  const dismiss = () => {
    localStorage.setItem(TOUR_KEY, '1');
    setVisible(false);
  };

  const isLast = step === STEPS.length - 1;

  return (
    <AnimatePresence>
      {visible && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
            onClick={dismiss}
          />

          {/* Card */}
          <motion.div
            key="card"
            initial={{ opacity: 0, scale: 0.95, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 16 }}
            transition={{ type: 'spring', stiffness: 320, damping: 28 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div className="pointer-events-auto w-full max-w-md rounded-2xl border border-slate-700/80 bg-slate-900/95 shadow-2xl shadow-black/40 backdrop-blur-md overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between px-6 pt-5 pb-3">
                <div className="flex items-center gap-2 text-amber-300">
                  <Sparkles className="h-4 w-4" />
                  <span className="text-xs font-semibold uppercase tracking-wider">
                    Demo walkthrough
                  </span>
                </div>
                <button
                  onClick={dismiss}
                  className="rounded-md p-1.5 text-slate-500 hover:text-slate-300 hover:bg-white/10 transition"
                  aria-label="Close tour"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Step indicator */}
              <div className="flex gap-1.5 px-6 pb-4">
                {STEPS.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setStep(i)}
                    className={`h-1 flex-1 rounded-full transition-all ${
                      i === step ? 'bg-amber-400' : 'bg-slate-700'
                    }`}
                    aria-label={`Go to step ${i + 1}`}
                  />
                ))}
              </div>

              {/* Content */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={step}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.18 }}
                  className="px-6 pb-6"
                >
                  <div className="flex items-start gap-4">
                    <span className="text-4xl leading-none mt-0.5" role="img" aria-label={STEPS[step].title}>
                      {STEPS[step].icon}
                    </span>
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-1">
                        {STEPS[step].title}
                      </h3>
                      <p className="text-sm leading-relaxed text-slate-400">
                        {STEPS[step].description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>

              {/* Footer */}
              <div className="flex items-center justify-between px-6 pb-5 gap-3">
                <button
                  onClick={dismiss}
                  className="text-xs text-slate-500 hover:text-slate-300 transition"
                >
                  Skip tour
                </button>
                <div className="flex gap-2">
                  {step > 0 && (
                    <button
                      onClick={() => setStep(step - 1)}
                      className="inline-flex items-center gap-1 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-white/10 transition"
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Back
                    </button>
                  )}
                  <button
                    onClick={isLast ? dismiss : () => setStep(step + 1)}
                    className="inline-flex items-center gap-1 rounded-lg bg-amber-500 hover:bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-950 transition"
                  >
                    {isLast ? 'Start exploring' : 'Next'}
                    {!isLast && <ChevronRight className="h-4 w-4" />}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
