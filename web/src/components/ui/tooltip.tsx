import * as React from "react"
import { cn } from "@/lib/utils"

interface TooltipProps {
  content: string
  children: React.ReactNode
  className?: string
}

export function Tooltip({ content, children, className }: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState(false)

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        className="cursor-help"
      >
        {children}
      </div>
      {isVisible && (
        <div className={cn(
          "absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 dark:bg-gray-700 rounded-lg shadow-lg",
          "bottom-full left-1/2 transform -translate-x-1/2 mb-2",
          "max-w-xs break-words",
          "before:content-[''] before:absolute before:top-full before:left-1/2 before:transform before:-translate-x-1/2",
          "before:border-4 before:border-transparent before:border-t-gray-900 dark:before:border-t-gray-700",
          className
        )}>
          {content}
        </div>
      )}
    </div>
  )
}