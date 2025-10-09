# Test leaderboard

Submit and track model performance via GitHub Issues. Results display automatically on GitHub Pages.

## Quick Start

**Students:** [Submit your results](../../issues/new?template=submission.yml) via GitHub Issues.
**Note**: Each student can submit multiple times to the leaderboard. But do not edit your submission as it will render only once, you can close it and open a new one.

**Admins:** Comment `/verify` on an issue to verify it, or close the issue to remove it

## Setup

1. **Enable GitHub Pages:** Settings → Pages → Source: `main` branch, `/docs` folder
2. **Set Permissions:** Settings → Actions → General → Workflow permissions: "Read and write permissions"

Leaderboard will be at: https://newturing.github.io/a2-leaderboard/

## How It Works

- Issue opened/edited → Leaderboard updated
- Admin comments `/verify` → Submission marked verified  
- Issue closed → Submission removed
