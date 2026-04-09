/**
 * Changelog Modal Template
 *
 * Adapt this to your project's UI library and styling system.
 * This template uses shadcn/ui Dialog + Tailwind CSS.
 *
 * Dependencies:
 *   - @/components/ui/dialog (shadcn)
 *   - @/lib/changelog-data (your structured data file)
 *   - react-markdown (if content is markdown strings)
 */

"use client"

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import {
  changelogReleases,
  getCurrentVersion,
} from "@/lib/changelog-data"

// If using markdown strings for content, uncomment:
// import ReactMarkdown from "react-markdown"

interface ChangelogModalProps {
  trigger?: React.ReactNode
}

export function ChangelogModal({ trigger }: ChangelogModalProps) {
  const [open, setOpen] = useState(false)
  const version = getCurrentVersion()

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger ?? (
          <button className="text-xs text-muted-foreground hover:text-foreground transition-colors">
            v{version}
          </button>
        )}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Changelog</DialogTitle>
        </DialogHeader>
        <ScrollArea className="h-[60vh] pr-4">
          {changelogReleases.map((release, index) => (
            <div key={release.version}>
              <div className="py-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold">{release.title}</h3>
                  <span className="text-sm text-muted-foreground">
                    {release.date}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {release.excerpt}
                </p>
                <div className="prose dark:prose-invert prose-sm">
                  {/* For JSX content: */}
                  {release.content}

                  {/* For markdown string content, replace above with: */}
                  {/* <ReactMarkdown>{release.content}</ReactMarkdown> */}
                </div>
              </div>
              {index < changelogReleases.length - 1 && <Separator />}
            </div>
          ))}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
