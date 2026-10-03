import unittest
from src.ingestion.chunker import (
    TranscriptChunker,
    format_seconds_to_timestamp,
    parse_timestamp_to_seconds,
)
from src.ingestion.transcriber import parse_srt, parse_vtt, parse_json_transcript


class TestChunkerTimestamps(unittest.TestCase):
    def test_timestamp_conversions(self):
        self.assertEqual(parse_timestamp_to_seconds("00:01:30"), 90.0)
        self.assertEqual(parse_timestamp_to_seconds("01:00:00"), 3600.0)
        self.assertEqual(parse_timestamp_to_seconds("02:15.500"), 135.5)
        self.assertEqual(parse_timestamp_to_seconds("00:01:23,456"), 83.456)

        self.assertEqual(format_seconds_to_timestamp(90), "01:30")
        self.assertEqual(format_seconds_to_timestamp(3665), "01:01:05")
        self.assertEqual(format_seconds_to_timestamp(0), "00:00")

    def test_parse_vtt_cues(self):
        vtt_content = """WEBVTT

00:00:01.000 --> 00:00:05.500
Welcome to this agentic RAG course lecture.

00:00:06.000 --> 00:00:12.000
Today we will cover video transcripts and guardrails.
"""
        segments = parse_vtt(vtt_content)
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0]["start_time"], "00:00:01.000")
        self.assertIn("Welcome to this agentic RAG course", segments[0]["text"])
        self.assertEqual(segments[1]["start_time"], "00:00:06.000")

    def test_parse_srt_cues(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
First line of the lecture.

2
00:00:05,000 --> 00:00:09,000
Second line explaining vector databases.
"""
        segments = parse_srt(srt_content)
        self.assertEqual(len(segments), 2)
        self.assertIn("First line", segments[0]["text"])
        self.assertIn("Second line", segments[1]["text"])

    def test_chunk_timestamped_segments(self):
        chunker = TranscriptChunker(chunk_size=100, chunk_overlap=20)
        segments = [
            {"start": 0.0, "end": 10.0, "text": "Segment one introduces RAG basics."},
            {"start": 10.5, "end": 25.0, "text": "Segment two explains chunking strategies and token lengths."},
            {"start": 25.5, "end": 40.0, "text": "Segment three dives deep into ChromaDB embeddings and similarity metrics."},
        ]

        chunks = chunker.chunk_timestamped_segments(
            segments,
            metadata={"video_id": "lesson_1", "title": "Intro to RAG"}
        )

        self.assertGreaterEqual(len(chunks), 1)
        for chunk in chunks:
            meta = chunk["metadata"]
            self.assertEqual(meta["video_id"], "lesson_1")
            self.assertIn("start_time", meta)
            self.assertIn("start_seconds", meta)
            self.assertIn("end_time", meta)
            self.assertIn("end_seconds", meta)
            self.assertLessEqual(meta["start_seconds"], meta["end_seconds"])
            self.assertGreater(len(chunk["text"]), 0)


if __name__ == "__main__":
    unittest.main()

