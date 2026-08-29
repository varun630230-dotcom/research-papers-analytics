"use client";

import { SourceInfo } from '@/types';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { BookOpen, ExternalLink, Quote, Search, ArrowUpDown } from 'lucide-react';
import { useState } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

interface SourcesTabProps {
  sources: SourceInfo[];
}

export function SourcesTab({ sources }: SourcesTabProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'year' | 'citations'>('citations');
  const [sortDesc, setSortDesc] = useState(true);

  if (!sources || sources.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <BookOpen className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">No sources available</h3>
        <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md">
          No citation sources are available for this project.
        </p>
      </div>
    );
  }

  const filteredSources = sources.filter(s => 
    s.title?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    s.authors?.some(a => a.toLowerCase().includes(searchTerm.toLowerCase())) ||
    s.venue?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedSources = [...filteredSources].sort((a, b) => {
    let valA, valB;
    if (sortBy === 'year') {
      valA = a.year || 0;
      valB = b.year || 0;
    } else {
      valA = a.citation_count || 0;
      valB = b.citation_count || 0;
    }
    
    if (valA < valB) return sortDesc ? 1 : -1;
    if (valA > valB) return sortDesc ? -1 : 1;
    return 0;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between gap-4 bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-200 dark:border-gray-800">
        <div className="relative flex-grow max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input 
            placeholder="Search by title, author, or venue..." 
            className="pl-9 bg-white dark:bg-gray-900"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500 font-medium">Sort by:</span>
          <div className="flex rounded-md shadow-sm">
            <Button
              variant={sortBy === 'citations' ? 'default' : 'outline'}
              size="sm"
              className={`rounded-r-none ${sortBy === 'citations' ? 'bg-blue-600 hover:bg-blue-700' : ''}`}
              onClick={() => {
                if (sortBy === 'citations') setSortDesc(!sortDesc);
                else { setSortBy('citations'); setSortDesc(true); }
              }}
            >
              Citations
              {sortBy === 'citations' && <ArrowUpDown className="w-3 h-3 ml-1.5 opacity-70" />}
            </Button>
            <Button
              variant={sortBy === 'year' ? 'default' : 'outline'}
              size="sm"
              className={`rounded-l-none border-l-0 ${sortBy === 'year' ? 'bg-blue-600 hover:bg-blue-700' : ''}`}
              onClick={() => {
                if (sortBy === 'year') setSortDesc(!sortDesc);
                else { setSortBy('year'); setSortDesc(true); }
              }}
            >
              Year
              {sortBy === 'year' && <ArrowUpDown className="w-3 h-3 ml-1.5 opacity-70" />}
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div className="text-sm text-gray-500 mb-2">
          Showing {sortedSources.length} of {sources.length} sources
        </div>
        
        {sortedSources.map((source, i) => (
          <Card key={i} className="hover:shadow-sm transition-shadow">
            <CardContent className="p-5 flex gap-4">
              <div className="hidden sm:flex text-gray-400 font-mono text-sm pt-1 w-8 flex-shrink-0">
                [{i + 1}]
              </div>
              <div className="flex-grow space-y-2">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2">
                  <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-lg font-medium text-blue-600 dark:text-blue-400 hover:underline leading-tight flex items-center gap-1.5">
                    {source.title}
                    <ExternalLink className="w-4 h-4 flex-shrink-0" />
                  </a>
                  {source.pdf_url && (
                    <a href={source.pdf_url} target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-red-600 hover:text-red-800 bg-red-50 px-2 py-1 rounded whitespace-nowrap flex items-center gap-1">
                      PDF
                    </a>
                  )}
                </div>
                
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {source.authors?.join(', ')}
                </p>
                
                <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-gray-500">
                  <span className="font-medium">{source.year || 'Unknown Year'}</span>
                  {source.venue && (
                    <span className="truncate max-w-xs">{source.venue}</span>
                  )}
                  {source.doi && (
                    <a href={`https://doi.org/${source.doi}`} target="_blank" rel="noopener noreferrer" className="hover:text-blue-500 transition-colors">
                      DOI: {source.doi}
                    </a>
                  )}
                  <span className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded text-gray-700 dark:text-gray-300">
                    <Quote className="w-3 h-3" />
                    {source.citation_count || 0} citations
                  </span>
                  {source.open_access && (
                    <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 dark:bg-green-900/20 dark:border-green-800">
                      Open Access
                    </Badge>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {sortedSources.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No sources match your search criteria.
          </div>
        )}
      </div>
    </div>
  );
}
