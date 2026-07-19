# Blog Automation Workflow

Automated daily blog post generation, WordPress publishing, Airtable tracking, and Slack notifications.

## How It Works

**Every day at 2 AM UTC:**
1. GitHub Actions runs the workflow
2. Blog post is generated based on topic rotation (7-day cycle)
3. Post is published to WordPress
4. Record is created in Airtable
5. Social copy is posted to Slack

## Setup Instructions

### 1. Airtable Setup

Create a new table in your Airtable base with these fields:

**Table Name:** `Daily Posts`

**Fields:**
- `Title` (Text) - Blog post title
- `Topic` (Single Select) - Topic from rotation
- `Date Published` (Date) - Publication date
- `Word Count` (Number) - Word count
- `WordPress URL` (URL) - Link to published post
- `Social Copy` (Long Text) - Social media text
- `Status` (Single Select) - Options: Draft, Published

### 2. GitHub Secrets Configuration

Add these secrets to your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**
