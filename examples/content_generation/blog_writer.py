#!/usr/bin/env python3
"""Blog Writer Example - Puter Python SDK.

Automated blog post generation with structure, SEO optimization, and multiple formats.
Perfect for content creators, marketers, and bloggers.
"""

import os
import re
from datetime import datetime

from puter import PuterAI


class BlogWriter:
    """AI-powered blog post generator."""

    def __init__(self):
        """Initialize the blog writer."""
        self.client = None

    def initialize(self, username=None, password=None):
        """Initialize the AI client."""
        username = username or os.getenv("PUTER_USERNAME")
        password = password or os.getenv("PUTER_PASSWORD")

        if not username or not password:
            raise ValueError("Please provide Puter.js credentials")

        self.client = PuterAI(username=username, password=password)
        self.client.login()

    def generate_blog_ideas(self, topic, count=5):
        """Generate blog post ideas for a topic."""
        prompt = """Generate {count} engaging blog post ideas about "{topic}".
        For each idea, provide:
        1. A catchy title
        2. A brief description (1-2 sentences)
        3. Target audience

        Format as a numbered list. Make the titles SEO-friendly and engaging."""

        response = self.client.chat(prompt)
        return response

    def create_outline(self, title, target_audience="general readers", word_count=1000):
        """Create a detailed blog post outline."""
        prompt = """Create a detailed outline for a blog post titled "{title}".

        Target audience: {target_audience}
        Target word count: {word_count} words

        Include:
        1. Hook/Introduction
        2. Main sections with subsections
        3. Key points to cover in each section
        4. Call-to-action ideas
        5. SEO keywords to focus on

        Make it engaging and well-structured."""

        response = self.client.chat(prompt)
        return response

    def write_introduction(self, title, outline_context=""):
        """Write an engaging introduction."""
        prompt = """Write an engaging introduction for a blog post titled "{title}".

        {f"Context from outline: {outline_context}" if outline_context else ""}

        The introduction should:
        - Hook the reader immediately
        - Clearly state what they'll learn
        - Be 150-200 words
        - Include a compelling reason to keep reading

        Write in a conversational, engaging tone."""

        response = self.client.chat(prompt)
        return response

    def write_section(self, section_title, context, word_count=300):
        """Write a detailed section of the blog post."""
        prompt = """Write a detailed section for a blog post with the heading
        "{section_title}".

        Context: {context}
        Target length: ~{word_count} words

        Requirements:
        - Provide valuable, actionable information
        - Use examples and practical tips
        - Include subheadings if needed
        - Write in an engaging, conversational tone
        - Make it scannable with bullet points or numbered lists where appropriate

        Focus on delivering real value to the reader."""

        response = self.client.chat(prompt)
        return response

    def write_conclusion(self, title, main_points):
        """Write a compelling conclusion with call-to-action."""
        prompt = """Write a compelling conclusion for a blog post titled "{title}".

        Main points covered: {main_points}

        The conclusion should:
        - Summarize key takeaways
        - Reinforce the main message
        - Include a strong call-to-action
        - Be 100-150 words
        - Leave the reader feeling inspired or motivated to act

        End with an engaging question or thought-provoking statement."""

        response = self.client.chat(prompt)
        return response

    def generate_seo_elements(self, title, content_preview):
        """Generate SEO elements for the blog post."""
        prompt = """Create SEO elements for a blog post titled "{title}".

        Content preview: {content_preview}

        Generate:
        1. Meta description (150-160 characters)
        2. 5-7 relevant keywords
        3. 3 alternative title suggestions for A/B testing
        4. Social media preview text (120 characters)
        5. Suggested tags/categories

        Focus on search intent and user value."""

        response = self.client.chat(prompt)
        return response

    def full_blog_post(self, topic, target_audience="general readers", word_count=1000):
        """Generate a complete blog post."""
        print(f"🚀 Generating blog post about '{topic}'...")

        # Step 1: Generate title ideas
        print("📝 Generating title ideas...")
        title_prompt = """Create 3 SEO-friendly, engaging blog post titles about
        "{topic}" for {target_audience}. Make them clickable and valuable."""

        titles_response = self.client.chat(title_prompt)
        print(f"Title ideas:\n{titles_response}\n")

        # Extract first title (simple approach)
        title_match = re.search(r"[1.][\s]*(.+)", titles_response)
        title = (
            title_match.group(1).strip()
            if title_match
            else f"The Ultimate Guide to {topic}"
        )
        print(f"✅ Selected title: {title}\n")

        # Step 2: Create outline
        print("📋 Creating outline...")
        outline = self.create_outline(title, target_audience, word_count)
        print("Outline created!\n")

        # Step 3: Write introduction
        print("✍️ Writing introduction...")
        intro = self.write_introduction(title, outline[:200])

        # Step 4: Write main sections
        print("📚 Writing main content...")
        sections = []

        # Simple section generation (in a real app, you'd parse the outline)
        section_topics = [
            f"What is {topic}?",
            f"Benefits of {topic}",
            f"How to Get Started with {topic}",
            f"Best Practices for {topic}",
            "Common Mistakes to Avoid",
        ]

        for section_topic in section_topics:
            print(f"  • Writing: {section_topic}")
            section_content = self.write_section(
                section_topic,
                f"This is part of a blog post about {topic} for {target_audience}",
                word_count // len(section_topics),
            )
            sections.append(f"## {section_topic}\n\n{section_content}")

        # Step 5: Write conclusion
        print("🎯 Writing conclusion...")
        main_points = ", ".join(section_topics)
        conclusion = self.write_conclusion(title, main_points)
        print("\\n=== CONCLUSION ===")
        print(conclusion)

        # Step 6: Generate SEO elements
        print("🔍 Generating SEO elements...")
        content_preview = intro[:200] + "..."
        seo_elements = self.generate_seo_elements(title, content_preview)
        print("\\n=== SEO ELEMENTS ===")
        print(seo_elements)

        # Combine everything
        full_post = """# {title}

{intro}

{chr(10).join(sections)}

## Conclusion

{conclusion}

---

## SEO Elements

{seo_elements}

---
*Generated by Puter Python SDK on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return full_post

    def save_post(self, content, filename=None):
        """Save blog post to a markdown file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"blog_post_{timestamp}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        return filename


def main():
    """Interactive blog writer."""
    print("✍️ AI Blog Writer - Puter Python SDK")
    print("=" * 45)

    try:
        writer = BlogWriter()
        print("Initializing AI writer...")
        writer.initialize()
        print("✅ Ready to write!\n")

        while True:
            print("🎯 What would you like to do?")
            print("1. Generate blog ideas")
            print("2. Create a blog outline")
            print("3. Write a complete blog post")
            print("4. Quit")

            choice = input("\nChoice (1-4): ").strip()

            if choice == "1":
                topic = input("Enter topic: ").strip()
                if topic:
                    print(f"\n💡 Blog ideas for '{topic}':")
                    print("-" * 40)
                    ideas = writer.generate_blog_ideas(topic)
                    print(ideas)
                    print()

            elif choice == "2":
                title = input("Enter blog post title: ").strip()
                audience = input(
                    "Target audience (or press Enter for 'general'): "
                ).strip()
                audience = audience or "general readers"

                if title:
                    print(f"\n📋 Outline for '{title}':")
                    print("-" * 50)
                    outline = writer.create_outline(title, audience)
                    print(outline)
                    print()

            elif choice == "3":
                topic = input("Enter blog topic: ").strip()
                audience = input(
                    "Target audience (or press Enter for 'general'): "
                ).strip()
                word_count = input(
                    "Target word count (or press Enter for 1000): "
                ).strip()

                audience = audience or "general readers"
                try:
                    word_count = int(word_count) if word_count else 1000
                except ValueError:
                    word_count = 1000

                if topic:
                    print(f"\n🚀 Creating full blog post about '{topic}'...")
                    print("This may take a few minutes...\n")

                    blog_post = writer.full_blog_post(topic, audience, word_count)

                    print("✅ Blog post completed!")

                    # Save option
                    save = input("\nSave to file? (y/n): ").strip().lower()
                    if save in ["y", "yes"]:
                        filename = writer.save_post(blog_post)
                        print(f"💾 Saved to {filename}")

                    # Preview option
                    preview = input("Show preview? (y/n): ").strip().lower()
                    if preview in ["y", "yes"]:
                        print("\n" + "=" * 60)
                        print("BLOG POST PREVIEW")
                        print("=" * 60)
                        print(
                            blog_post[:1000] + "..."
                            if len(blog_post) > 1000
                            else blog_post
                        )
                        print("=" * 60)
                    print()

            elif choice == "4":
                print("\n👋 Thanks for using the AI Blog Writer!")
                break

            else:
                print("❌ Invalid choice. Please try again.\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("• Valid Puter.js credentials")
        print("• Internet connection")


if __name__ == "__main__":
    main()
