interface TranscriptEntry {
  text: string;
  start: number;
  duration: number;
}

interface TranscriptViewerProps {
  transcript: TranscriptEntry[];
}

export function TranscriptViewer({ transcript }: TranscriptViewerProps) {
  // Function to format time in MM:SS format
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h2 className="mb-4 text-xl font-bold">Transcript</h2>
      <div className="p-4 bg-white rounded-lg shadow max-h-96 overflow-y-auto">
        {transcript.map((entry, index) => (
          <div key={index} className="mb-2">
            <span className="text-gray-500">
              {formatTime(entry.start)} - {formatTime(entry.start + entry.duration)}
            </span>
            <p>{entry.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
} 