/**
 * Changelog Version Trigger Template
 *
 * A small version badge that opens the changelog modal or links to the changelog page.
 * Adapt styling to match your project's design system.
 */

"use client"

import { getCurrentVersion } from "@/lib/changelog-data"
import { ChangelogModal } from "@/components/changelog-modal"

/**
 * Option A: Opens a modal (recommended for sidebar/footer placement)
 */
export function ChangelogTrigger() {
  const version = getCurrentVersion()

  return (
    <ChangelogModal
      trigger={
        <button
          className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
          title="View changelog"
        >
          v{version}
        </button>
      }
    />
  )
}

/**
 * Option B: Links to a /changelog page (use if you have a dedicated page)
 */
// import Link from "next/link"
//
// export function ChangelogTrigger() {
//   const version = getCurrentVersion()
//
//   return (
//     <Link
//       href="/changelog"
//       className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
//       title="View changelog"
//     >
//       v{version}
//     </Link>
//   )
// }
