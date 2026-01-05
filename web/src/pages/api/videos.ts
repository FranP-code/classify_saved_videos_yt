import type { APIRoute } from 'astro';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { parseCSV } from '../../utils/csvParser';

export const GET: APIRoute = async () => {
  try {
    // Look for CSV file in the project root (outside web folder)
    const csvPath = join(process.cwd(), '..', 'video_classifications.csv');
    
    if (!existsSync(csvPath)) {
      return new Response(
        JSON.stringify({ 
          error: 'CSV file not found',
          message: 'video_classifications.csv not found in project root',
          path: csvPath
        }), 
        {
          status: 404,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    }

    const csvContent = readFileSync(csvPath, 'utf-8');
    const videos = parseCSV(csvContent);

    return new Response(JSON.stringify({ videos }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error reading CSV file:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Failed to read CSV file',
        message: error instanceof Error ? error.message : 'Unknown error'
      }), 
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
};