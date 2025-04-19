/**
 * 直接测试后端API的工具函数
 * 用法: 在浏览器控制台中导入并调用:
 * 
 * import { testDirectAPI } from '@/app/directTest';
 * testDirectAPI('视频ID', 'detailed', 'zh');
 */

export async function testDirectAPI(
  videoId: string,
  summaryType: string = 'detailed',
  language: string = 'zh'
) {
  try {
    // 直接调用后端API，不经过Next.js代理
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
    
    // 获取原始响应文本
    const responseText = await response.text();
    
    // 尝试解析JSON
    try {
      const data = JSON.parse(responseText);
      return { success: true, data };
    } catch (jsonError) {
      return { 
        success: false, 
        error: '解析JSON失败', 
        errorDetails: jsonError,
        responseText: responseText.substring(0, 500) + '...' // 只返回前500字符
      };
    }
  } catch (error) {
    return { success: false, error };
  }
}

// 添加一个简便的全局测试函数，可以在浏览器控制台直接调用
if (typeof window !== 'undefined') {
  (window as any).testYouTubeSummaryAPI = (
    videoId: string, 
    summaryType: string = 'detailed', 
    language: string = 'zh'
  ) => {
    return testDirectAPI(videoId, summaryType, language);
  };
} 