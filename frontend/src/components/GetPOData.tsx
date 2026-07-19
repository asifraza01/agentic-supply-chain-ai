// components/DataFetcher.tsx
'use client';

import { useEffect } from 'react';

interface POFetcherProps {
  onPOFetched: (data: any) => void;
}

export default function POFetcher({ onPOFetched }: POFetcherProps) {
  useEffect(() => {
    async function fetchFromFastAPI() {
      try {
        // Point this to your FastAPI server URL
        const response = await fetch("http://127.0.0.1:8001/api/stats");
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        onPOFetched(data); 
      } catch (error) {
        console.error('FastAPI Fetch failed:', error);
      }
    };

    fetchFromFastAPI();
    const interval = setInterval(fetchFromFastAPI, 3000); // Fetch every 3 seconds

    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  return null; // This component doesn't render anything


}
