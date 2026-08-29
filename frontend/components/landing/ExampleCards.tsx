import React from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Lightbulb, Stethoscope, Shield, Leaf, BookOpen, CreditCard } from 'lucide-react'

const EXAMPLES = [
  { text: 'AI-based crop disease detection using smartphones', icon: Leaf },
  { text: 'Detect cyberbullying using multimodal AI', icon: Shield },
  { text: 'AI system for early disease prediction', icon: Stethoscope },
  { text: 'Smart waste management using computer vision', icon: Leaf },
  { text: 'AI assistant for personalized education', icon: BookOpen },
  { text: 'Fraud detection for digital payments', icon: CreditCard },
]

interface ExampleCardsProps {
  onSelect: (text: string) => void
  disabled?: boolean
}

export function ExampleCards({ onSelect, disabled }: ExampleCardsProps) {
  return (
    <div className="w-full max-w-4xl mx-auto mt-12 animate-fade-in opacity-0" style={{ animationDelay: '0.5s', animationFillMode: 'forwards' }}>
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-4 text-center uppercase tracking-wider">
        Or start with an example
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {EXAMPLES.map((example, i) => (
          <Card 
            key={i} 
            variant="default"
            className={`cursor-pointer transition-all hover:border-primary-300 hover:shadow-md dark:hover:border-primary-700 ${disabled ? 'opacity-50 pointer-events-none' : ''}`}
            onClick={() => onSelect(example.text)}
          >
            <CardContent className="p-4 flex items-start gap-3">
              <div className="p-2 bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-lg shrink-0">
                <example.icon className="w-4 h-4" />
              </div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 leading-snug">
                {example.text}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
