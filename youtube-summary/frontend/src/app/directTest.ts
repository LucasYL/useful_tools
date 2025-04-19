/**
 * Function to directly test the backend API
 * Usage: Import and call in browser console:
 * 
 * import { testDirectAPI } from '@/app/directTest';
 * testDirectAPI('videoID', 'detailed', 'zh');
 */

export async function testDirectAPI(
  videoId: string,
  summaryType: string = 'detailed',
  language: string = 'zh'
) {
  try {
    // Call backend API directly, bypassing Next.js proxy
    const response = await fetch('http://localhost:8000/api/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        video_id: videoId,
        summary_type: summaryType,
        language: language
      }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      return { success: false, error: errorText };
    }
    
    // Get the raw response text
    const responseText = await response.text();
    
    // Try to parse JSON
    try {
      const data = JSON.parse(responseText);
      return { success: true, data };
    } catch (jsonError) {
      return { 
        success: false, 
        error: 'Failed to parse JSON', 
        errorDetails: jsonError,
        responseText: responseText.substring(0, 500) + '...' // Only return first 500 characters
      };
    }
  } catch (error) {
    return { success: false, error };
  }
}

// Add a convenient global test function, can be called directly in browser console
if (typeof window !== 'undefined') {
  (window as any).testYouTubeSummaryAPI = (
    videoId: string, 
    summaryType: string = 'detailed', 
    language: string = 'zh'
  ) => {
    return testDirectAPI(videoId, summaryType, language);
  };
} 