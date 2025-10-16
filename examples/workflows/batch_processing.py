#!/usr/bin/env python3
"""
Batch Processing Example - Puter Python SDK

Efficiently process multiple tasks using AI with rate limiting, error handling,
and progress tracking. Perfect for content analysis, data processing, and automation.
"""

import asyncio
import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, List

from puter import PuterAI


class BatchProcessor:
    """AI-powered batch processing with progress tracking."""

    def __init__(self, rate_limit_requests=5, rate_limit_period=60):
        self.client = None
        self.results = []
        self.errors = []
        self.processed_count = 0
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_period = rate_limit_period

    def initialize(self, username=None, password=None):
        """Initialize the AI client with rate limiting."""
        username = username or os.getenv("PUTER_USERNAME")
        password = password or os.getenv("PUTER_PASSWORD")

        if not username or not password:
            raise ValueError("Please provide Puter.js credentials")

        self.client = PuterAI(
            username=username,
            password=password,
            rate_limit_requests=self.rate_limit_requests,
            rate_limit_period=self.rate_limit_period,
        )
        self.client.login()

    def process_sentiment_analysis(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts."""
        print(f"🎭 Analyzing sentiment for {len(texts)} texts...")

        results = []
        for i, text in enumerate(texts, 1):
            try:
                prompt = """Analyze the sentiment of this text and provide:
                1. Overall sentiment (positive/negative/neutral)
                2. Confidence score (0-100%)
                3. Key emotions detected
                4. Brief explanation (1 sentence)

                Text: "{text}"

                Format as JSON: {{"sentiment": "", "confidence": 0, "emotions": [], "explanation": ""}}"""

                response = self.client.chat(prompt)

                # Try to extract JSON from response
                try:
                    # Simple JSON extraction (in production, use more robust parsing)
                    json_start = response.find("{")
                    json_end = response.rfind("}") + 1
                    if json_start != -1 and json_end > json_start:
                        result_data = json.loads(response[json_start:json_end])
                    else:
                        result_data = {
                            "sentiment": "unknown",
                            "confidence": 0,
                            "emotions": [],
                            "explanation": response[:100],
                        }
                except json.JSONDecodeError:
                    result_data = {
                        "sentiment": "error",
                        "confidence": 0,
                        "emotions": [],
                        "explanation": response[:100],
                    }

                result = {
                    "id": i,
                    "original_text": text,
                    "analysis": result_data,
                    "processed_at": datetime.now().isoformat(),
                }

                results.append(result)
                print(
                    f"  ✅ {i}/{len(texts)} - {result_data.get('sentiment', 'unknown').upper()}"
                )

            except Exception as e:
                error = {
                    "id": i,
                    "original_text": text,
                    "error": str(e),
                    "processed_at": datetime.now().isoformat(),
                }
                self.errors.append(error)
                print(f"  ❌ {i}/{len(texts)} - Error: {e}")

            self.processed_count += 1

        return results

    def process_text_summarization(
        self, texts: List[str], max_length=100
    ) -> List[Dict[str, Any]]:
        """Summarize multiple texts."""
        print(f"📝 Summarizing {len(texts)} texts...")

        results = []
        for i, text in enumerate(texts, 1):
            try:
                prompt = """Summarize this text in exactly {max_length} words or less.
                Keep the key information and main points.

                Text: "{text}"

                Summary:"""

                response = self.client.chat(prompt)

                result = {
                    "id": i,
                    "original_text": text,
                    "summary": response.strip(),
                    "original_length": len(text.split()),
                    "summary_length": len(response.strip().split()),
                    "processed_at": datetime.now().isoformat(),
                }

                results.append(result)
                print(
                    f"  ✅ {i}/{len(texts)} - {len(text.split())} → {len(response.strip().split())} words"
                )

            except Exception as e:
                error = {
                    "id": i,
                    "original_text": text,
                    "error": str(e),
                    "processed_at": datetime.now().isoformat(),
                }
                self.errors.append(error)
                print(f"  ❌ {i}/{len(texts)} - Error: {e}")

            self.processed_count += 1

        return results

    def process_translation(
        self, texts: List[str], target_language="Spanish"
    ) -> List[Dict[str, Any]]:
        """Translate multiple texts."""
        print(f"🌍 Translating {len(texts)} texts to {target_language}...")

        results = []
        for i, text in enumerate(texts, 1):
            try:
                prompt = """Translate this text to {target_language}.
                Maintain the original meaning and tone.

                Text: "{text}"

                Translation:"""

                response = self.client.chat(prompt)

                result = {
                    "id": i,
                    "original_text": text,
                    "translated_text": response.strip(),
                    "target_language": target_language,
                    "processed_at": datetime.now().isoformat(),
                }

                results.append(result)
                print(f"  ✅ {i}/{len(texts)} - Translated")

            except Exception as e:
                error = {
                    "id": i,
                    "original_text": text,
                    "error": str(e),
                    "processed_at": datetime.now().isoformat(),
                }
                self.errors.append(error)
                print(f"  ❌ {i}/{len(texts)} - Error: {e}")

            self.processed_count += 1

        return results

    async def async_batch_process(
        self, texts: List[str], task_type="sentiment"
    ) -> List[Dict[str, Any]]:
        """Process multiple texts asynchronously for better performance."""
        print(f"🚀 Async processing {len(texts)} texts ({task_type})...")

        async def process_single(text, index):
            try:
                if task_type == "sentiment":
                    prompt = """Analyze sentiment: "{text}"
                    Return JSON: {{"sentiment": "positive/negative/neutral", "score": 0.0}}"""
                elif task_type == "summary":
                    prompt = """Summarize in 50 words: "{text}"""
                else:
                    prompt = """Process this text: "{text}"""

                response = await self.client.async_chat(prompt)

                return {
                    "id": index,
                    "original_text": text,
                    "result": response,
                    "task_type": task_type,
                    "processed_at": datetime.now().isoformat(),
                }

            except Exception as e:
                return {
                    "id": index,
                    "original_text": text,
                    "error": str(e),
                    "task_type": task_type,
                    "processed_at": datetime.now().isoformat(),
                }

        # Process all texts concurrently
        tasks = [process_single(text, i + 1) for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)

        # Separate successful results from errors
        successful_results = [r for r in results if "error" not in r]
        error_results = [r for r in results if "error" in r]

        self.errors.extend(error_results)
        self.processed_count += len(results)

        print(
            f"✅ Completed: {len(successful_results)} successful, {len(error_results)} errors"
        )
        return successful_results

    def save_results(self, results: List[Dict[str, Any]], filename=None, format="json"):
        """Save processing results to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = "json" if format == "json" else "csv"
            filename = f"batch_results_{timestamp}.{extension}"

        if format == "json":
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "metadata": {
                            "processed_count": self.processed_count,
                            "error_count": len(self.errors),
                            "timestamp": datetime.now().isoformat(),
                        },
                        "results": results,
                        "errors": self.errors,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

        elif format == "csv":
            if results:
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    fieldnames = results[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(results)

        return filename

    def get_stats(self):
        """Get processing statistics."""
        return {
            "total_processed": self.processed_count,
            "errors": len(self.errors),
            "success_rate": (self.processed_count - len(self.errors))
            / max(self.processed_count, 1)
            * 100,
        }


def main():
    """Interactive batch processing demo."""
    print("⚡ AI Batch Processor - Puter Python SDK")
    print("=" * 50)

    try:
        processor = BatchProcessor(rate_limit_requests=3, rate_limit_period=10)
        print("Initializing batch processor...")
        processor.initialize()
        print("✅ Ready for batch processing!\n")

        # Sample data
        sample_texts = [
            "I absolutely love this new product! It's amazing and works perfectly.",
            "This service is terrible. I'm very disappointed with the quality.",
            "The weather today is quite nice, not too hot or cold.",
            "Artificial intelligence is revolutionizing how we work and live.",
            "I'm not sure about this decision. It could go either way.",
            "The restaurant had excellent food but poor service.",
            "Technology continues to advance at an incredible pace.",
            "This movie was neither good nor bad, just average.",
        ]

        while True:
            print("🎯 Batch Processing Options:")
            print("1. Sentiment Analysis")
            print("2. Text Summarization")
            print("3. Translation")
            print("4. Async Processing Demo")
            print("5. Load custom data from file")
            print("6. Quit")

            choice = input("\nChoice (1-6): ").strip()

            if choice == "1":
                print(
                    f"\n📊 Processing {len(sample_texts)} texts for sentiment analysis..."
                )
                results = processor.process_sentiment_analysis(sample_texts)

                if results:
                    filename = processor.save_results(results)
                    print(f"\n💾 Results saved to {filename}")

                    stats = processor.get_stats()
                    print(f"📈 Stats: {stats['success_rate']:.1f}% success rate")

            elif choice == "2":
                print(f"\n📝 Processing {len(sample_texts)} texts for summarization...")
                results = processor.process_text_summarization(
                    sample_texts, max_length=30
                )

                if results:
                    filename = processor.save_results(results)
                    print(f"\n💾 Results saved to {filename}")

            elif choice == "3":
                language = (
                    input("Target language (default: Spanish): ").strip() or "Spanish"
                )
                print(f"\n🌍 Translating {len(sample_texts)} texts to {language}...")
                results = processor.process_translation(sample_texts, language)

                if results:
                    filename = processor.save_results(results)
                    print(f"\n💾 Results saved to {filename}")

            elif choice == "4":
                print("\n🚀 Async processing demo...")
                results = asyncio.run(
                    processor.async_batch_process(sample_texts[:4], "sentiment")
                )

                if results:
                    filename = processor.save_results(results)
                    print(f"\n💾 Results saved to {filename}")

            elif choice == "5":
                filename = input("Enter filename (txt/csv): ").strip()
                if os.path.exists(filename):
                    with open(filename, "r", encoding="utf-8") as f:
                        if filename.endswith(".csv"):
                            reader = csv.reader(f)
                            texts = [row[0] for row in reader if row]  # First column
                        else:
                            texts = [line.strip() for line in f if line.strip()]

                    print(f"📁 Loaded {len(texts)} texts from {filename}")
                    task = (
                        input("Task (sentiment/summary/translation): ").strip().lower()
                    )

                    if task == "sentiment":
                        results = processor.process_sentiment_analysis(texts)
                    elif task == "summary":
                        results = processor.process_text_summarization(texts)
                    elif task == "translation":
                        lang = input("Target language: ").strip() or "Spanish"
                        results = processor.process_translation(texts, lang)
                    else:
                        print("❌ Invalid task type")
                        continue

                    if results:
                        output_file = processor.save_results(results)
                        print(f"\n💾 Results saved to {output_file}")
                else:
                    print("❌ File not found")

            elif choice == "6":
                break

            else:
                print("❌ Invalid choice")

            print("\n" + "-" * 50)

        final_stats = processor.get_stats()
        print("\n📊 Final Statistics:")
        print(f"• Total processed: {final_stats['total_processed']}")
        print(f"• Success rate: {final_stats['success_rate']:.1f}%")
        print(f"• Errors: {final_stats['errors']}")
        print("\n👋 Thanks for using the batch processor!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
