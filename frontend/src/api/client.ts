// 1. The Analyzer API with the new timeout failsafe
export const analyzeCode = async (code: string, language: string) => {
  const controller = new AbortController();
 const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes

  try {
    const response = await fetch('http://127.0.0.1:8000/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ code, language }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Server Error (${response.status}): Could not analyze code.`);
    }

    return await response.json();
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('The AI model took too long to respond. The server might be overloaded.');
    }
    throw new Error(`Connection failed. Ensure the Python backend is running on port 8000. Detail: ${error.message}`);
  }
};

// 2. The Model Card API (restored)
export const fetchModelCard = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/model-card');
    if (!response.ok) throw new Error('Failed to fetch model card');
    return await response.json();
  } catch (error) {
    console.error('Error fetching model card:', error);
    throw error;
  }
};