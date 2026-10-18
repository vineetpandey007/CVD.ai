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

// 3. Bulk ZIP File Upload API
export const analyzeBulkFiles = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minutes for large codebases

  try {
    const response = await fetch('http://127.0.0.1:8000/api/analyze-bulk', {
      method: 'POST',
      // Notice we do NOT set 'Content-Type' here. 
      // The browser automatically sets it with the correct boundary for FormData.
      body: formData,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Server Error (${response.status}): Could not analyze zip file.`);
    }

    return await response.json();
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('The bulk scan took too long to respond. Try uploading a smaller repository.');
    }
    throw new Error(`Bulk upload failed. Detail: ${error.message}`);
  }
};

// 4. DuckDB Scan History - Fetch All Logs
export const fetchScanHistory = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/history');
  if (!response.ok) {
    throw new Error('Failed to fetch scan history.');
  }
  return await response.json();
};

// 5. DuckDB Scan History - Fetch Specific Report Detail
export const fetchScanDetail = async (id: string) => {
  const response = await fetch(`http://127.0.0.1:8000/api/history/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch scan detail.');
  }
  return await response.json();
};