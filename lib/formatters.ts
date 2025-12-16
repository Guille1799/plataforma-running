/**
 * formatters.ts - Utility functions for formatting data
 */

/**
 * Format pace in seconds per km to MM:SS/km format
 */
export function formatPace(secondsPerKm: number | null | undefined): string {
  if (!secondsPerKm || secondsPerKm <= 0) return '--:--';

  const minutes = Math.floor(secondsPerKm / 60);
  const seconds = Math.floor(secondsPerKm % 60);

  return `${minutes}:${seconds.toString().padStart(2, '0')}/km`;
}

/**
 * Format duration in seconds to HH:MM:SS or MM:SS
 */
export function formatDuration(seconds: number | null | undefined): string {
  if (!seconds || seconds <= 0) return '--:--';

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format distance in meters to km with 2 decimals
 */
export function formatDistance(meters: number | null | undefined): string {
  if (!meters || meters <= 0) return '0.00 km';

  const km = meters / 1000;
  return `${km.toFixed(2)} km`;
}

/**
 * Format distance in meters to km (short version, no decimals if >= 1km)
 */
export function formatDistanceShort(meters: number | null | undefined): string {
  if (!meters || meters <= 0) return '0 km';

  const km = meters / 1000;

  if (km >= 1) {
    return `${Math.round(km)} km`;
  }

  return `${Math.round(meters)} m`;
}

/**
 * Format heart rate with bpm unit
 */
export function formatHeartRate(bpm: number | null | undefined): string {
  if (!bpm || bpm <= 0) return '-- bpm';
  return `${Math.round(bpm)} bpm`;
}

/**
 * Format calories
 */
export function formatCalories(calories: number | null | undefined): string {
  if (!calories || calories <= 0) return '0 kcal';
  return `${Math.round(calories)} kcal`;
}

/**
 * Format elevation in meters
 */
export function formatElevation(meters: number | null | undefined): string {
  if (!meters || meters <= 0) return '0 m';
  return `${Math.round(meters)} m`;
}

/**
 * Format date to relative time (e.g., "2 hours ago", "Yesterday")
 */
export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const past = new Date(date);
  const diffMs = now.getTime() - past.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;

  return formatDate(date);
}

/**
 * Format date to readable string (e.g., "Nov 13, 2025")
 */
export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

/**
 * Format date with time (e.g., "Nov 13, 2025 at 10:30 AM")
 */
export function formatDateTime(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Format time only (e.g., "10:30 AM")
 */
export function formatTime(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Get zone color based on HR zone number (1-5)
 */
export function getZoneColor(zone: number | string): string {
  const zoneNum = typeof zone === 'string' ? parseInt(zone.replace(/\D/g, '')) : zone;

  switch (zoneNum) {
    case 1:
      return 'text-green-500 bg-green-500/10 border-green-500/20';
    case 2:
      return 'text-lime-500 bg-lime-500/10 border-lime-500/20';
    case 3:
      return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
    case 4:
      return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
    case 5:
      return 'text-red-500 bg-red-500/10 border-red-500/20';
    default:
      return 'text-gray-500 bg-gray-500/10 border-gray-500/20';
  }
}

/**
 * Get zone name based on zone number
 */
export function getZoneName(zone: number | string): string {
  const zoneNum = typeof zone === 'string' ? parseInt(zone.replace(/\D/g, '')) : zone;

  switch (zoneNum) {
    case 1:
      return 'Recovery';
    case 2:
      return 'Aerobic';
    case 3:
      return 'Tempo';
    case 4:
      return 'Threshold';
    case 5:
      return 'VO2 Max';
    default:
      return 'Unknown';
  }
}

/**
 * Get running level label
 */
export function getRunningLevelLabel(level: string | undefined): string {
  if (!level) return 'Not set';
  return level.charAt(0).toUpperCase() + level.slice(1);
}

/**
 * Get coaching style label
 */
export function getCoachingStyleLabel(style: string | undefined): string {
  if (!style) return 'Not set';
  return style.charAt(0).toUpperCase() + style.slice(1);
}

/**
 * Calculate pace from distance and duration
 */
export function calculatePace(distanceMeters: number, durationSeconds: number): number {
  if (distanceMeters <= 0 || durationSeconds <= 0) return 0;
  const km = distanceMeters / 1000;
  return durationSeconds / km;
}

/**
 * Format percentage
 */
export function formatPercentage(value: number): string {
  return `${Math.round(value)}%`;
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
}

/**
 * Enrich workout with computed properties for dashboard compatibility
 */
export function enrichWorkout(workout: any): any {
  return {
    ...workout,
    distance_km: workout.distance_meters / 1000,
    avg_pace_min_km: workout.avg_pace,
    date: workout.start_time,
  };
}

/**
 * Enrich array of workouts
 */
export function enrichWorkouts(workouts: any[]): any[] {
  if (!Array.isArray(workouts)) {
    return [];
  }
  return workouts.map(enrichWorkout);
}
