/**
 * Global type declarations for window extensions
 */

declare global {
  interface Window {
    __API_LOGS__?: Array<{
      type: 'REQUEST' | 'RESPONSE' | 'ERROR' | 'REQUEST_ERROR';
      timestamp: string;
      method?: string;
      url?: string;
      status?: number;
      statusText?: string;
      errorMessage?: string;
      responseData?: any;
      requestData?: any;
      data?: any;
      [key: string]: any;
    }>;
  }
}

export {};
