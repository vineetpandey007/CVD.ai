export function AmbientBackground() {
  const codeSnippets = [
    // Python
    `def analyze_sentiment(text):
  tokens = tokenize(text)
  embeddings = model.encode(tokens)
  return classifier.predict(embeddings)`,
    
    // JavaScript
    `const processNLP = async (input) => {
  const response = await fetch('/api/nlp');
  const result = await response.json();
  return result.sentiment;
};`,
    
    // Java
    `public class TextProcessor {
  private NLPModel model;
  public Sentiment analyze(String text) {
    Token[] tokens = tokenize(text);
    return model.classify(tokens);
  }
}`,
    
    // SQL
    `SELECT sentiment, COUNT(*) as freq
FROM analysis_results
WHERE language = 'en'
GROUP BY sentiment
ORDER BY freq DESC;`,
    
    // C++
    `void processText(const string& input) {
  vector<Token> tokens = tokenize(input);
  float score = model.predict(tokens);
  emit_result(score);
}`,
    
    // Go
    `func analyzeText(text string) Sentiment {
  tokens := Tokenize(text)
  embedding := encoder.Encode(tokens)
  return classifier.Predict(embedding)
}`,
  ];

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-black">
      {/* Blurred AI Analyzer Image */}
      <div className="absolute inset-0 overflow-hidden">
        <img 
          src="https://images.unsplash.com/photo-1677442d019cecf8978b4491a7305e8223c74665565b337f3ad1e527aab32e69?w=1200&h=800&fit=crop" 
          alt="AI Analyzer"
          className="w-full h-full object-cover blur-3xl opacity-20"
        />
      </div>

      {/* Floating code snippets */}
      <div className="absolute inset-0 overflow-hidden">
        {codeSnippets.map((code, i) => (
          <div
            key={i}
            className="absolute font-mono text-xs opacity-0 animate-[codeFloat_12s_ease-in-out_infinite] text-white/30 whitespace-pre pointer-events-none"
            style={{
              left: `${(i % 3) * 35 + 10}%`,
              top: `${(i % 2) * 40 + 20}%`,
              animationDelay: `${i * 1.5}s`,
              animationDuration: `${12 + i * 1.5}s`,
              maxWidth: '200px',
              lineHeight: '1.4',
            }}
          >
            {code}
          </div>
        ))}
      </div>
      
      {/* Subtle radial fade */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle at center, transparent 30%, rgba(0,0,0,0.4) 100%)`,
        }}
      ></div>

      {/* Top fade */}
      <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-black to-transparent pointer-events-none"></div>

      {/* Bottom fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black to-transparent pointer-events-none"></div>
    </div>
  );
}
