/**
 * Changelog Data Template
 *
 * Structured changelog data for UI rendering.
 * Content uses markdown strings — render with react-markdown or similar.
 *
 * Adapt the import path for package.json to match your project's setup.
 */

import packageJson from "../package.json"

export interface ChangelogRelease {
  version: string
  title: string
  date: string
  excerpt: string
  content: string // Markdown string
}

export const changelogReleases: ChangelogRelease[] = [
  {
    version: "1.0.0",
    title: "v1.0.0: Initial Release",
    date: "April 9, 2026",
    excerpt: "First tracked release.",
    content: `### Added
- Initial changelog system setup
- Version tracking with semantic versioning`,
  },
]

/**
 * Get the current app version from package.json.
 * Import this wherever you need to display the version.
 */
export function getCurrentVersion(): string {
  return packageJson.version
}

/**
 * Get the latest version documented in the changelog.
 * Useful for checking if package.json and changelog are in sync.
 */
export function getLatestChangelogVersion(): string {
  return changelogReleases[0]?.version ?? "1.0.0"
}
