#!/usr/bin/env python3
"""
Daily blog post generator and publisher
Generates blog content based on topic rotation, publishes to WordPress, tracks in Airtable, notifies Slack
"""

import os
import json
import requests
import base64
from datetime import datetime
from typing import Dict, Tuple

# Configuration
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')
AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK')

TOPIC_ROTATION = [
    "Adobe Premiere Pro",
    "After Effects",
    "Adobe Audition",
    "Character Animator",
    "Filmmaking in General",
    "AI & Filmmaking",
    "Post-Production Topics"
]

def get_todays_topic() -> str:
    """Determine today's topic based on day of year"""
    day_of_year = datetime.now().timetuple().tm_yday
    topic_index = (day_of_year - 1) % len(TOPIC_ROTATION)
    return TOPIC_ROTATION[topic_index]

def generate_blog_content(topic: str) -> Tuple[str, str, int]:
    """Generate blog post content (title, content, word_count)"""
    prompts = {
        "Adobe Premiere Pro": {
            "title": "Mastering Adobe Premiere Pro: Workflows That Save Hours",
            "outline": "Dive deep into Premiere Pro workflows for efficient editing"
        },
        "After Effects": {
            "title": "After Effects Secrets: Motion Design Techniques Everyone Should Know",
            "outline": "Advanced motion design techniques in After Effects"
        },
        "Adobe Audition": {
            "title": "Audio Post with Audition: Professional Sound Design in Your DAW",
            "outline": "Professional audio workflows using Adobe Audition"
        },
        "Character Animator": {
            "title": "Character Animator: Real-Time Animation That Actually Works",
            "outline": "Practical uses of Character Animator for content creators"
        },
        "Filmmaking in General": {
            "title": "The Filmmaker's Workflow: Pre-Production to Final Delivery",
            "outline": "Complete filmmaking workflow from concept to delivery"
        },
        "AI & Filmmaking": {
            "title": "AI in Filmmaking: What's Useful, What's Hype, What's Next",
            "outline": "Honest assessment of AI tools for filmmakers"
        },
        "Post-Production Topics": {
            "title": "Post-Production Mastery: Color, Sound, and Final Delivery",
            "outline": "Complete post-production workflow and best practices"
        }
    }

    post_data = prompts.get(topic, prompts["Adobe Premiere Pro"])
    content = f"""<h2>{post_data['outline']}</h2>

<p>Today's focus: {topic}</p>

<p>The workflow matters more than the tool. Whether you're using {topic} or any other software, understanding the fundamentals will make you a better creator.</p>

<h3>Key Takeaways</h3>
<ul>
<li>Efficiency compounds over time</li>
<li>Learn the tool's workflow, not just the features</li>
<li>Practice with real projects</li>
</ul>

<p>Ready to level up? Subscribe to the newsletter for real-world workflows and honest tool reviews.</p>"""

    title = post_data["title"]
    word_count = len(content.split())

    return title, content, word_count

def publish_to_wordpress(title: str, content: str) -> Dict:
    """Publish post to WordPress via REST API"""
    auth_string = base64.b64encode(
        f"{WORDPRESS_USER}:{WORDPRESS_PASSWORD}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    response = requests.post(
        f"{WORDPRESS_URL}/wp-json/wp/v2/posts",
        json=payload,
        headers=headers,
        timeout=30
    )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"WordPress API error: {response.status_code} - {response.text}")

def create_airtable_record(title: str, topic: str, url: str, word_count: int) -> Dict:
    """Create record in Airtable tracking table"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    fields = {
        "Title": title,
        "Topic": [topic],
        "Date Published": datetime.now().strftime("%Y-%m-%d"),
        "Word Count": word_count,
        "WordPress URL": url,
        "Status": ["Published"]
    }

    payload = {"records": [{"fields": fields}]}

    response = requests.post(
        f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Daily%20Posts",
        json=payload,
        headers=headers,
        timeout=30
    )

    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"Airtable API error: {response.status_code} - {response.text}")

def post_to_slack(title: str, url: str, topic: str) -> bool:
    """Post social copy notification to Slack"""
    social_copy = f"""🎬 **NEW BLOG POST**

**{title}**

Topic: {topic}
Read: {url}

#AdobeCreativeCloud #Filmmaking"""

    payload = {
        "text": social_copy,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": social_copy
                }
            }
        ]
    }

    response = requests.post(
        SLACK_WEBHOOK,
        json=payload,
        timeout=30
    )

    return response.status_code == 200

def main():
    """Main workflow: generate, publish, track, notify"""
    try:
        print("🚀 Daily blog automation started")

        topic = get_todays_topic()
        print(f"📝 Today's topic: {topic}")

        title, content, word_count = generate_blog_content(topic)
        print(f"✍️  Generated: {title} ({word_count} words)")

        wp_response = publish_to_wordpress(title, content)
        post_id = wp_response.get('id')
        post_url = wp_response.get('link')
        print(f"✅ Published to WordPress: {post_url}")

        airtable_response = create_airtable_record(title, topic, post_url, word_count)
        print(f"📊 Airtable record created")

        slack_success = post_to_slack(title, post_url, topic)
        if slack_success:
            print(f"💬 Slack notification sent")

        print(f"::set-output name=title::{title}")
        print(f"::set-output name=url::{post_url}")

        print("✨ Daily blog automation complete!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
