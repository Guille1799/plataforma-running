/**
 * Log Viewer - Utility to view and export API logs
 * 
 * Usage in console:
 * - logViewer.show() - Show all logs
 * - logViewer.showErrors() - Show only errors
 * - logViewer.showRequests(url) - Show requests to specific URL
 * - logViewer.export() - Export logs as JSON
 * - logViewer.clear() - Clear logs
 */

export const logViewer = {
  /**
   * Get all logs
   */
  getAll(): any[] {
    if (typeof window === 'undefined' || !window.__API_LOGS__) {
      return [];
    }
    return [...window.__API_LOGS__];
  },

  /**
   * Show all logs in console
   */
  show(): void {
    const logs = this.getAll();
    console.group('📋 API Logs (All)');
    logs.forEach((log, index) => {
      const emoji = log.type === 'ERROR' ? '❌' : log.type === 'REQUEST' ? '🔵' : '✅';
      console.log(`${emoji} [${index}] ${log.method} ${log.url} - ${log.type}`, log);
    });
    console.groupEnd();
    console.log(`Total logs: ${logs.length}`);
  },

  /**
   * Show only errors
   */
  showErrors(): void {
    const logs = this.getAll().filter(log => log.type === 'ERROR' || log.type === 'REQUEST_ERROR');
    console.group('❌ API Errors');
    logs.forEach((log, index) => {
      console.error(`[${index}] ${log.method} ${log.url}`, log);
    });
    console.groupEnd();
    console.log(`Total errors: ${logs.length}`);
  },

  /**
   * Show requests to a specific URL pattern
   */
  showRequests(urlPattern: string): void {
    const logs = this.getAll().filter(log => 
      log.url?.includes(urlPattern) || log.fullURL?.includes(urlPattern)
    );
    console.group(`🔍 API Logs matching "${urlPattern}"`);
    logs.forEach((log, index) => {
      const emoji = log.type === 'ERROR' ? '❌' : log.type === 'REQUEST' ? '🔵' : '✅';
      console.log(`${emoji} [${index}] ${log.method} ${log.url}`, log);
    });
    console.groupEnd();
    console.log(`Found ${logs.length} logs matching "${urlPattern}"`);
  },

  /**
   * Show recent logs (last N)
   */
  showRecent(count: number = 10): void {
    const logs = this.getAll().slice(-count);
    console.group(`📋 API Logs (Last ${count})`);
    logs.forEach((log, index) => {
      const emoji = log.type === 'ERROR' ? '❌' : log.type === 'REQUEST' ? '🔵' : '✅';
      console.log(`${emoji} ${log.timestamp} ${log.method} ${log.url} - ${log.status || log.type}`, log);
    });
    console.groupEnd();
  },

  /**
   * Export logs as JSON
   */
  export(): string {
    const logs = this.getAll();
    const json = JSON.stringify(logs, null, 2);
    console.log('📤 Exported logs:');
    console.log(json);
    return json;
  },

  /**
   * Clear all logs
   */
  clear(): void {
    if (typeof window !== 'undefined' && window.__API_LOGS__) {
      window.__API_LOGS__.length = 0;
      console.log('🗑️ Logs cleared');
    }
  },

  /**
   * Get logs summary for debugging
   */
  getSummary(): {
    total: number;
    requests: number;
    responses: number;
    errors: number;
    recentErrors: any[];
  } {
    const logs = this.getAll();
    return {
      total: logs.length,
      requests: logs.filter(l => l.type === 'REQUEST').length,
      responses: logs.filter(l => l.type === 'RESPONSE').length,
      errors: logs.filter(l => l.type === 'ERROR' || l.type === 'REQUEST_ERROR').length,
      recentErrors: logs
        .filter(l => l.type === 'ERROR' || l.type === 'REQUEST_ERROR')
        .slice(-5),
    };
  },

  /**
   * Show summary
   */
  summary(): void {
    const summary = this.getSummary();
    console.group('📊 API Logs Summary');
    console.log(`Total: ${summary.total}`);
    console.log(`Requests: ${summary.requests}`);
    console.log(`Responses: ${summary.responses}`);
    console.log(`Errors: ${summary.errors}`);
    if (summary.recentErrors.length > 0) {
      console.group('Recent Errors:');
      summary.recentErrors.forEach((err, i) => {
        console.error(`[${i}] ${err.method} ${err.url}`, err);
      });
      console.groupEnd();
    }
    console.groupEnd();
  },

  /**
   * Share logs with AI assistant (copies to clipboard and prints)
   */
  share(): void {
    const logs = this.getAll();
    const summary = this.getSummary();
    
    // Create a formatted report
    const report = {
      timestamp: new Date().toISOString(),
      summary: summary,
      recentLogs: logs.slice(-20), // Last 20 logs
      errors: logs.filter(l => l.type === 'ERROR' || l.type === 'REQUEST_ERROR'),
    };
    
    const jsonReport = JSON.stringify(report, null, 2);
    
    // Copy to clipboard if available
    if (navigator.clipboard) {
      navigator.clipboard.writeText(jsonReport).then(() => {
        console.log('📋 Logs copied to clipboard! Paste them here to share with the AI assistant.');
      }).catch(() => {
        console.log('⚠️ Could not copy to clipboard, but logs are printed below.');
      });
    }
    
    // Print formatted report
    console.group('📤 LOGS TO SHARE WITH AI ASSISTANT');
    console.log(jsonReport);
    console.groupEnd();
    console.log('\n💡 TIP: Copy the JSON above and paste it in your message to the AI assistant.');
    
    return jsonReport;
  },
};

// Make available globally for easy access
if (typeof window !== 'undefined') {
  (window as any).logViewer = logViewer;
}
